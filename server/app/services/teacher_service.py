import os
import uuid
import traceback
from datetime import datetime
from sqlite3 import IntegrityError
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

# 项目内部导入
from app import db
from app.extensions import db
from app.models.user import User, class_user  # class_user为用户-班级关联表（多对多）
from app.models.class_model import Class
from app.models.report import Report
from app.models.score import Score
from app.models.course_material import CourseMaterial
from app.models.video import Video
from app.utils.file_utils import save_file, get_file_size  # 外部工具函数


def get_classes_by_teacher(teacher_id):
    """获取教师管理的所有班级"""
    return Class.query.join(class_user).filter(class_user.c.user_id == teacher_id).all()

def create_class(teacher_id, data):
    """创建新班级"""
    try:
        existing_class = Class.query.filter_by(course_code=data.get('course_code')).first()
        if existing_class:
            raise ValueError(f"课程代码 '{data.get('course_code')}' 已存在，请使用不同的课程代码")
        new_class = Class(
            name=data.get('name'),
            course_code=data.get('course_code'),
            academic_year=data.get('academic_year'),
            description=data.get('description')
        )
        db.session.add(new_class)
        # 将教师添加到班级
        teacher = User.query.get(teacher_id)
        if teacher:
            new_class.users.append(teacher)
        
        db.session.commit()
        return new_class
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def update_class(teacher_id, class_id, data):
    """更新班级信息"""
    class_ = Class.query.join(class_user).filter(
        Class.class_id == class_id,
        class_user.c.user_id == teacher_id
    ).first()
    
    if not class_:
        raise ValueError("Class not found or you don't have permission")
    
    try:
        class_.name = data.get('name', class_.name)
        class_.course_code = data.get('course_code', class_.course_code)
        class_.academic_year = data.get('academic_year', class_.academic_year)
        class_.description = data.get('description', class_.description)
        
        db.session.commit()
        return class_
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def delete_class(teacher_id, class_id):
    """删除班级"""
    class_ = Class.query.join(class_user).filter(
        Class.class_id == class_id,
        class_user.c.user_id == teacher_id
    ).first()
    
    if not class_:
        raise ValueError("Class not found or you don't have permission")
    
    try:
        # 删除班级与用户的关联
        db.session.execute(class_user.delete().where(class_user.c.class_id == class_id))
        db.session.delete(class_)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def get_students_in_class(class_id):
    """获取班级中的所有学生"""
    return User.query.join(class_user).filter(
        class_user.c.class_id == class_id,
        User.role == 'student'
    ).all()

def import_students_from_excel(class_id, file_path, file_ext):
    """从Excel或CSV文件导入学生"""
    try:
        if file_ext in ['.xlsx', '.xls']:
            # 读取Excel文件
            df = pd.read_excel(file_path)
        elif file_ext == '.csv':
            # 读取CSV文件，尝试不同的编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            if df is None:
                raise ValueError("无法读取CSV文件，请检查文件编码")
        else:
            raise ValueError(f"不支持的文件类型: {file_ext}")
        
        # 清理列名：去除空格和特殊字符
        df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)
        
        # 定义可能的列名变体
        possible_columns = {
            '学号': ['学号', 'student_id', 'student id', '学号ID', '学生学号'],
            '姓名': ['姓名', 'name', 'username', '学生姓名', '学生名字'],
            '邮箱': ['邮箱', 'email', 'mail', '电子邮件', '学生邮箱']
        }
        
        # 映射实际列名到标准列名
        column_mapping = {}
        for standard_col, possible_names in possible_columns.items():
            for possible_name in possible_names:
                if possible_name in df.columns:
                    column_mapping[standard_col] = possible_name
                    break
        
        # 检查必要的列是否存在
        required_columns = ['学号', '姓名']
        missing_columns = []
        for col in required_columns:
            if col not in column_mapping:
                missing_columns.append(col)
        
        if missing_columns:
            raise ValueError(f"文件缺少必要列: {missing_columns}。找到的列: {df.columns.tolist()}")
        
        # 重命名列为标准名称
        reverse_mapping = {v: k for k, v in column_mapping.items()}
        df = df.rename(columns=reverse_mapping)
        
        # 清理数据：去除空格，处理NaN值
        df = df.fillna('')
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        
        # 去除重复行（基于学号）
        df = df.drop_duplicates(subset=['学号'], keep='first')
        
        imported_count = 0
        added_to_class_count = 0
        skipped_count = 0
        error_count = 0
        imported_students = []
        
        for index, row in df.iterrows():
            try:
                # 跳过空行或学号为空的行
                if pd.isna(row['学号']) or str(row['学号']).strip() in ['', 'nan', 'NaN', 'None']:
                    skipped_count += 1
                    continue
                    
                student_id = str(row['学号']).strip()
                username = str(row['姓名']).strip() if pd.notna(row.get('姓名')) and str(row.get('姓名')).strip() not in ['', 'nan', 'NaN', 'None'] else f"学生_{student_id}"
                
                # 处理邮箱
                email = None
                if '邮箱' in df.columns and pd.notna(row.get('邮箱')) and str(row.get('邮箱')).strip() not in ['', 'nan', 'NaN', 'None']:
                    email = str(row.get('邮箱')).strip()
                
                # 首先检查学生是否已存在（基于学号）
                existing_student = User.query.filter_by(student_id=student_id).first()
                
                if existing_student:
                    # 更严格的检查：学生是否已经在班级中
                    existing_relation = db.session.query(class_user).filter_by(
                        class_id=class_id, 
                        user_id=existing_student.user_id
                    ).first()
                    
                    if existing_relation:
                        # 学生已经在班级中，跳过
                        skipped_count += 1
                        print(f"学生已在班级中: {student_id}")
                        continue  # 明确跳过后续处理
                    
                    # 添加班级关联（学生存在但不在班级中）
                    try:
                        db.session.execute(
                            class_user.insert().values(
                                class_id=class_id, 
                                user_id=existing_student.user_id,
                                join_date=datetime.utcnow()
                            )
                        )
                        added_to_class_count += 1
                        print(f"添加现有学生到班级: {student_id}")
                    except IntegrityError:
                        # 如果出现唯一性约束错误，说明学生已经在班级中
                        db.session.rollback()
                        skipped_count += 1
                        print(f"学生已在班级中（约束错误）: {student_id}")
                        continue
                        
                else:
                     # 学生不存在，创建新学生
                    # 确保用户名唯一
                    base_username = username
                    counter = 1
                    final_username = base_username
                    
                    # 检查用户名是否已存在，如果存在则添加数字后缀
                    while User.query.filter_by(username=final_username).first():
                        final_username = f"{base_username}_{counter}"
                        counter += 1
                    
                    # 如果没有提供邮箱，使用默认邮箱
                    if not email:
                        email = f"{student_id}@example.com"
                    
                    # 确保邮箱唯一
                    final_email = email
                    counter = 1
                    while User.query.filter_by(email=final_email).first():
                        final_email = f"{student_id}_{counter}@example.com"
                        counter += 1
                    
                    student = User(
                        username=final_username,
                        student_id=student_id,
                        email=final_email,
                        role='student'
                    )
                    # 设置密码为学号
                    student.set_password(student_id)
                    
                    db.session.add(student)
                    db.session.flush()  # 获取user_id
                    
                    # 关联班级
                    db.session.execute(
                        class_user.insert().values(
                            class_id=class_id, 
                            user_id=student.user_id,
                            join_date=datetime.utcnow()
                        )
                    )
                    
                    imported_count += 1
                    imported_students.append(student)
                    print(f"创建新学生: {student_id}")

            except IntegrityError as e:
                db.session.rollback()
                error_count += 1
                print(f"完整性错误处理学生 {student_id}: {str(e)}")
                continue
            except Exception as e:
                db.session.rollback()
                error_count += 1
                print(f"处理学生 {student_id} 时发生错误: {str(e)}")
                continue
        
        db.session.commit()
        
        return {
            'imported_count': imported_count,
            'added_to_class_count': added_to_class_count,
            'skipped_count': skipped_count,
            'error_count': error_count,
            'total_count': len(df),
            'imported_students': [s.to_dict() for s in imported_students]
        }
        
    except Exception as e:
        db.session.rollback()
        print(f"导入过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e

def reset_student_password(teacher_id, student_id):
    """重置学生密码为学号"""
    # 验证教师是否有权限管理这个学生
    teacher_classes = get_classes_by_teacher(teacher_id)
    student = User.query.filter_by(user_id=student_id, role='student').first()
    
    if not student:
        raise ValueError("Student not found")
    
    # 检查学生是否在教师的任何一个班级中
    has_permission = False
    for class_ in teacher_classes:
        if student in class_.users:
            has_permission = True
            break
    
    if not has_permission:
        raise ValueError("You don't have permission to reset this student's password")
    
    try:
        # 重置密码为学号
        default_password = student.student_id or str(uuid.uuid4())
        student.set_password(default_password)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def upload_course_material(file, title, description, user_id, course_id):
    """上传课程资料"""
    if not file:
        raise ValueError("没有文件被上传")
    
    # 安全处理文件名
    filename = secure_filename(file.filename)
    
    # 确保上传目录存在
    upload_dir = os.path.join('app', 'uploads', 'materials')
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # 保存文件
    file.save(file_path)
    file_size = os.path.getsize(file_path)
    file_type = ext[1:] if ext.startswith('.') else ext
    
    # 创建课程资料记录
    material = CourseMaterial(
        title=title,
        description=description,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        upload_time=datetime.now(),
        user_id=user_id,
        course_id=course_id
    )
    
    db.session.add(material)
    db.session.commit()
    
    return material

def get_course_materials(course_id):
    """获取课程的所有资料"""
    return CourseMaterial.query.filter_by(course_id=course_id).all()

def delete_course_material(material_id):
    """删除课程资料"""
    material = CourseMaterial.query.get(material_id)
    if not material:
        raise ValueError("资料不存在")
    
    # 删除文件
    if os.path.exists(material.file_path):
        os.remove(material.file_path)
    
    # 删除数据库记录
    db.session.delete(material)
    db.session.commit()


def upload_video(file, title, description, user_id, course_id):
    """上传视频文件"""
    if not file:
        return {"success": False, "message": "没有文件被上传"}
        
    # 安全处理文件名
    filename = secure_filename(file.filename)
        
    # 确保上传目录存在
    upload_dir = os.path.join('app', 'uploads', 'videos')
    os.makedirs(upload_dir, exist_ok=True)
        
    # 保存文件
    file_path = save_file(file, upload_dir)
    file_size = get_file_size(file_path)
        
    # 创建视频记录
    video = Video(
        title=title,
        description=description,
        file_path=file_path,
        file_size=file_size,
        upload_time=datetime.now(),
        user_id=user_id,
        course_id=course_id
        )
        
    db.session.add(video)
    db.session.commit()
        
    return {"success": True, "message": "视频上传成功", "video": video.to_dict()}
    

def get_videos_by_course(course_id):
    """获取课程的所有视频"""
    videos = Video.query.filter_by(course_id=course_id).all()
    return [video.to_dict() for video in videos]
    
def get_video_by_id(video_id):
    """根据ID获取视频"""
    video = Video.query.get(video_id)
    if not video:
        return None
    return video.to_dict()
    

def update_video(video_id, title=None, description=None):
    """更新视频信息"""
    video = Video.query.get(video_id)
    if not video:
        return {"success": False, "message": "视频不存在"}
        
    if title:
        video.title = title
    if description:
        video.description = description
        
    db.session.commit()
    return {"success": True, "message": "视频信息更新成功", "video": video.to_dict()}
    
def delete_video(video_id):
    """删除视频"""
    video = Video.query.get(video_id)
    if not video:
        raise ValueError("视频不存在")
        
        # 删除文件
    try:
        if os.path.exists(video.file_path):
           os.remove(video.file_path)
    except Exception as e:
        return {"success": False, "message": f"删除文件失败: {str(e)}"}
        # 删除数据库记录
    db.session.delete(video)
    db.session.commit()    
    return {"success": True, "message": "视频删除成功"}


def get_reports_by_class(class_id, status='submitted'):
    """获取班级报告列表"""
    return Report.query.join(User).join(class_user).filter(
        class_user.c.class_id == class_id,
        Report.status == status
    ).order_by(Report.created_at.desc()).all()

def review_report(teacher_id, report_id, data):
    """批阅报告"""
    report = Report.query.get(report_id)
    if not report:
        raise ValueError("Report not found")
    
    try:
        # 更新报告状态和评分
        report.status = 'reviewed'
        report.score = data.get('score')
        report.feedback = data.get('feedback')
        report.updated_at = datetime.utcnow()
        
        # 创建评分记录
        new_score = Score(
            score_value=data.get('score'),
            feedback=data.get('feedback'),
            report_id=report_id,
            teacher_id=teacher_id
        )
        db.session.add(new_score)
        
        db.session.commit()
        return report
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def get_class_score_statistics(class_id):
    """获取班级成绩统计信息"""
    students = get_students_in_class(class_id)
    student_ids = [s.user_id for s in students]
    
    # 获取这些学生的所有报告成绩
    reports = Report.query.filter(
        Report.user_id.in_(student_ids),
        Report.status == 'reviewed',
        Report.score.isnot(None)
    ).all()
    
    return students, reports

def get_student_scores_with_reports(class_id):
    """获取班级学生成绩及报告信息"""
    students = get_students_in_class(class_id)
    
    student_scores = []
    for student in students:
        # 获取学生的最新报告成绩
        latest_report = Report.query.filter(
            Report.user_id == student.user_id,
            Report.status == 'reviewed'
        ).order_by(Report.submitted_at.desc()).first()
        
        student_scores.append({
            'student': student.to_dict(),
            'report': latest_report.to_dict() if latest_report else None,
            'score': latest_report.score if latest_report else None
        })
    
    return student_scores

    """获取学生所在班级的课程内容"""
    try:
        # 获取学生所在的班级
        student = User.query.get(student_id)
        if not student:
            return {
                'success': False, 
                'error': '学生不存在',
                'contents': []
            }
        
        class_ids = [cls.class_id for cls in student.classes]
        
        # 如果没有班级，返回空数组
        if not class_ids:
            return {
                'success': True, 
                'contents': []
            }
        
        # 查询课程内容
        query = CourseContent.query.filter(
            CourseContent.class_id.in_(class_ids),
            CourseContent.is_published == True
        )
        
        if content_type:
            query = query.filter_by(content_type=content_type)
        
        contents = query.order_by(CourseContent.created_at.desc()).all()
        
        # 序列化结果
        serialized_contents = []
        for content in contents:
            content_dict = content.to_dict()
            # 确保所有字段都有值
            content_dict.setdefault('video_url', '')
            content_dict.setdefault('body', '')
            content_dict.setdefault('attachments', [])
            serialized_contents.append(content_dict)
        
        return {
            'success': True, 
            'contents': serialized_contents
        }
    except Exception as e:
        # 记录错误日志
        import traceback
        current_app.logger.error(f"获取学生内容失败: {str(e)}\n{traceback.format_exc()}")
        return {
            'success': False, 
            'error': str(e),
            'contents': []
        }