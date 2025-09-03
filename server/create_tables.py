from app import create_app
from app.extensions import db
from app.models.video import Video
from app.models.course_material import CourseMaterial

app = create_app()
with app.app_context():
    db.create_all()
    print("数据库表创建成功！")