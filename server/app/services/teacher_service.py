from app.extensions import db
from app.models.user import User,class_user
from app.models.class_model import Class
from app.models.report import Report
from app.models.score import Score
from app.models.content import CourseContent
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash
from datetime import datetime
import openpyxl
import uuid

def get_classes_by_teacher(teacher_id):
    """获取教师管理的所有班级"""
    return Class.query.join(class_user).filter(class_user.c.user_id == teacher_id).all()

def create_class(teacher_id, data):
    """创建新班级"""
    try:
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

def import_students_from_excel(class_id, file_path):
    """从Excel导入学生"""
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        
        students = []
        for row in sheet.iter_rows(min_row=2, values_only=True):  # 跳过标题行
            student_id, username, email = row[:3]  # 假设前三列是学号、姓名、邮箱
            
            # 检查学生是否已存在
            student = User.query.filter_by(student_id=student_id).first()
            if not student:
                # 创建新学生账户，默认密码为学号
                password = generate_password_hash(str(student_id))
                student = User(
                    username=username,
                    password_hash=password,
                    email=email,
                    role='student',
                    student_id=student_id
                )
                db.session.add(student)
            
            # 检查学生是否已在班级中
            class_ = Class.query.get(class_id)
            if class_ and student not in class_.users:
                class_.users.append(student)
            
            students.append(student)
        
        db.session.commit()
        return students
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Error importing students: {str(e)}")

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

def get_contents_by_class(class_id):
    """获取班级内容列表"""
    return CourseContent.query.filter_by(class_id=class_id).order_by(CourseContent.created_at.desc()).all()

def create_content(teacher_id, data):
    """创建新内容"""
    try:
        new_content = CourseContent(
            title=data.get('title'),
            content_type=data.get('content_type'),
            body=data.get('body'),
            video_url=data.get('video_url'),
            is_published=data.get('is_published', False),
            author_id=teacher_id,
            class_id=data.get('class_id')
        )
        db.session.add(new_content)
        db.session.commit()
        return new_content
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def update_content(teacher_id, content_id, data):
    """更新内容"""
    content = CourseContent.query.filter_by(content_id=content_id, author_id=teacher_id).first()
    if not content:
        raise ValueError("Content not found or you don't have permission")
    
    try:
        content.title = data.get('title', content.title)
        content.content_type = data.get('content_type', content.content_type)
        content.body = data.get('body', content.body)
        content.video_url = data.get('video_url', content.video_url)
        content.is_published = data.get('is_published', content.is_published)
        content.updated_at = datetime.utcnow()
        
        db.session.commit()
        return content
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def delete_content(teacher_id, content_id):
    """删除内容"""
    content = CourseContent.query.filter_by(content_id=content_id, author_id=teacher_id).first()
    if not content:
        raise ValueError("Content not found or you don't have permission")
    
    try:
        db.session.delete(content)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

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

def get_scores_by_class(class_id):
    """获取班级成绩列表"""
    return Report.query.join(User).join(class_user).filter(
        class_user.c.class_id == class_id,
        Report.status == 'reviewed'
    ).order_by(Report.score.desc()).all()