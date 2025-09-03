# server/app/services/recommendation_service.py
import json
from sqlalchemy import func
from app.models.content import CourseContent
from app.models.video_history import VideoWatchHistory 
from app.extensions import db

class RecommendationService:
    
    @staticmethod
    def get_video_recommendations(current_video_id, user_id=None, limit=5):
        """
        获取视频推荐
        :param current_video_id: 当前观看的视频ID
        :param user_id: 用户ID（用于未来协同过滤）
        :param limit: 返回推荐数量
        :return: 推荐视频列表
        """
        current_video = CourseContent.query.get(current_video_id)  # 修改这里
        if not current_video or current_video.content_type != 'video':
            return []
        
        try:
            current_tags = json.loads(current_video.tags)
        except json.JSONDecodeError:
            current_tags = []
        
        # 基础查询：同一班级的其他视频
        base_query = CourseContent.query.filter(  # 修改这里
            CourseContent.class_id == current_video.class_id,
            CourseContent.content_type == 'video',  # 只推荐视频
            CourseContent.content_id != current_video_id
        )
        
        recommendations = []
        
        # 策略1: 标签相似度匹配（主要策略）
        if current_tags:
            tagged_videos = base_query.filter(CourseContent.tags != '[]').all()  # 修改这里
            
            for video in tagged_videos:
                try:
                    video_tags = json.loads(video.tags)
                except json.JSONDecodeError:
                    continue
                
                similarity = RecommendationService._calculate_similarity(current_tags, video_tags)
                if similarity > 0.1:  # 相似度阈值
                    recommendations.append({
                        'video': video,
                        'score': similarity,
                        'reason': '标签相似',
                        'matched_tags': list(set(current_tags) & set(video_tags))
                    })
            
            # 按相似度排序
            recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # 策略2: 如果没有标签推荐或推荐不足，用同班级最新视频补充
        if len(recommendations) < limit:
            recent_videos = base_query.order_by(CourseContent.created_at.desc()).limit(limit).all()  # 修改这里
            for video in recent_videos:
                # 避免重复添加
                if not any(rec['video'].content_id == video.content_id for rec in recommendations):
                    recommendations.append({
                        'video': video,
                        'score': 0.5,  # 默认分数
                        'reason': '同班级最新',
                        'matched_tags': []
                    })
        
        # 格式化返回结果
        formatted_recommendations = []
        for rec in recommendations[:limit]:
            video_dict = rec['video'].to_dict()
            video_dict.update({
                'recommend_reason': rec['reason'],
                'similarity_score': rec['score'],
                'matched_tags': rec['matched_tags']
            })
            formatted_recommendations.append(video_dict)
        
        return formatted_recommendations
    
    @staticmethod
    def _calculate_similarity(tags1, tags2):
        """计算Jaccard相似度"""
        set1 = set(tags1)
        set2 = set(tags2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0

# 创建单例
recommendation_service = RecommendationService()