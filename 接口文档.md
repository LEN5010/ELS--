# 英语学习系统 API 接口文档

## 目录
- [系统概述](#系统概述)
- [环境配置](#环境配置)
- [认证机制](#认证机制)
- [通用响应格式](#通用响应格式)
- [错误码说明](#错误码说明)
- [API接口列表](#api接口列表)
  - [用户认证](#用户认证)
  - [用户管理](#用户管理)
  - [学习资源](#学习资源)
  - [测验系统](#测验系统)
  - [社区功能](#社区功能)
  - [管理员功能](#管理员功能)
  - [日志系统](#日志系统)

---

## 系统概述

英语学习系统是一个基于Flask的RESTful API，提供词汇学习、语法教程、听力练习、测验系统、社区讨论等功能。

### 技术栈
- **后端**: Flask + Python 3.13
- **数据库**: MySQL (主要业务数据) + MongoDB (日志数据)
- **认证**: JWT Token
- **部署**: 开发环境端口 5000/5001

### 系统架构
```
MySQL数据库 (ELS)
├── 用户认证表 (user_auth)
├── 用户资料表 (user_profile)
├── 学习资源表 (vocab, grammar, listening)
├── 测验相关表 (quiz, quiz_question, quiz_result)
├── 社区相关表 (post, comment)
└── 学习进度表 (progress)

MongoDB数据库 (language_app_logs)
└── 活动日志集合 (activity_logs)
```

---

## 环境配置

### 基础URL
- **开发环境**: `http://localhost:5000` 或 `http://localhost:5001`
- **API前缀**: `/api`

### 数据库配置
```
MySQL: localhost:3306/ELS
MongoDB: mongodb://localhost:27017/language_app_logs
```

---

## 认证机制

系统使用JWT Token进行身份认证。

### Token获取
通过登录接口获取Token，有效期24小时。

### Token使用
在请求头中添加：
```
Authorization: Bearer <your_jwt_token>
```

### 权限等级
- **普通用户** (student): 基础学习功能
- **管理员** (admin): 所有功能 + 后台管理

---

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误信息",
  "data": null
}
```

---

## 错误码说明

| HTTP状态码 | 说明 |
|-----------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（Token无效或过期） |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## API接口列表

### 用户认证

#### 1. 用户注册
```
POST /api/auth/register
```

**请求参数**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "nickname": "用户昵称"  // 可选，默认为邮箱前缀
}
```

**响应示例**
```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "user_id": 1,
    "email": "user@example.com",
    "nickname": "用户昵称"
  }
}
```

#### 2. 用户登录
```
POST /api/auth/login
```

**请求参数**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应示例**
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "user_id": 1,
    "email": "user@example.com",
    "nickname": "用户昵称",
    "role": "student"
  }
}
```

#### 3. 用户登出
```
POST /api/auth/logout
```

**请求头**
```
Authorization: Bearer <token>
```

**响应示例**
```json
{
  "success": true,
  "message": "登出成功",
  "data": null
}
```

---

### 用户管理

#### 1. 获取用户资料
```
GET /api/user/profile
```

**请求头**
```
Authorization: Bearer <token>
```

**响应示例**
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "user_id": 1,
    "email": "user@example.com",
    "nickname": "用户昵称",
    "gender": "U",
    "birthday": null,
    "role": "student",
    "myps": "个人简介",
    "created_at": "2025-09-22T04:55:00"
  }
}
```

#### 2. 更新用户资料
```
PUT /api/user/profile
```

**请求参数**
```json
{
  "nickname": "新昵称",
  "gender": "M",  // M/F/U
  "birthday": "1990-01-01",
  "myps": "个人简介"
}
```

#### 3. 修改密码
```
PUT /api/user/password
```

**请求参数**
```json
{
  "old_password": "旧密码",
  "new_password": "新密码"
}
```

#### 4. 获取学习进度
```
GET /api/user/progress
```

**响应示例**
```json
{
  "success": true,
  "data": {
    "vocab_learned": 150,
    "grammar_learned": 25,
    "listening_done": 30,
    "last_update": "2025-09-22T04:55:00"
  }
}
```

---

### 学习资源

#### 1. 获取词汇列表
```
GET /api/learning/vocab
```

**查询参数**
- `level`: 难度等级 (A1/A2/B1/B2/C1/C2)
- `page`: 页码，默认1
- `per_page`: 每页数量，默认20

**响应示例**
```json
{
  "success": true,
  "data": {
    "total": 500,
    "page": 1,
    "per_page": 20,
    "data": [
      {
        "word_id": 1,
        "word": "hello",
        "meaning": "你好",
        "example": "Hello, world!",
        "level": "A1"
      }
    ]
  }
}
```

#### 2. 获取语法教程列表
```
GET /api/learning/grammar
```

**查询参数**
- `level`: 难度等级
- `page`: 页码
- `per_page`: 每页数量

#### 3. 获取听力材料列表
```
GET /api/learning/listening
```

**查询参数**
- `level`: 难度等级
- `page`: 页码
- `per_page`: 每页数量

#### 4. 获取单个词汇详情
```
GET /api/learning/vocab/{word_id}
```

#### 5. 标记学习进度
```
POST /api/learning/progress
```

**请求参数**
```json
{
  "content_type": "vocab",  // vocab/grammar/listening
  "content_id": 123,
  "action": "completed"     // started/completed/reviewed
}
```

---

### 测验系统

#### 1. 获取测验列表
```
GET /api/quiz/list
```

**查询参数**
- `quiz_type`: 测验类型 (vocab/grammar/listening)
- `page`: 页码
- `per_page`: 每页数量

**响应示例**
```json
{
  "success": true,
  "data": {
    "total": 50,
    "page": 1,
    "per_page": 10,
    "data": [
      {
        "quiz_id": 1,
        "quiz_type": "vocab",
        "title": "A1词汇测试",
        "total_points": 100
      }
    ]
  }
}
```

#### 2. 获取测验详情
```
GET /api/quiz/{quiz_id}
```

**响应示例**
```json
{
  "success": true,
  "data": {
    "quiz_id": 1,
    "quiz_type": "vocab",
    "title": "A1词汇测试",
    "total_points": 100,
    "questions": [
      {
        "question_id": 1,
        "question": "What does 'hello' mean?",
        "option_a": "你好",
        "option_b": "再见",
        "option_c": "谢谢",
        "option_d": "对不起",
        "score": 10
      }
    ]
  }
}
```

#### 3. 提交测验答案
```
POST /api/quiz/{quiz_id}/submit
```

**请求参数**
```json
{
  "answers": [
    {
      "question_id": 1,
      "selected_option": "A"
    }
  ]
}
```

**响应示例**
```json
{
  "success": true,
  "data": {
    "result_id": 123,
    "score": 85,
    "correct_count": 17,
    "total_count": 20,
    "accuracy": 85.0,
    "level": "Good",
    "details": [
      {
        "question_id": 1,
        "correct": true,
        "selected": "A",
        "correct_answer": "A",
        "score": 10
      }
    ]
  }
}
```

#### 4. 获取测验历史
```
GET /api/quiz/results
```

**查询参数**
- `quiz_id`: 特定测验ID（可选）
- `page`: 页码
- `per_page`: 每页数量

---

### 社区功能

#### 1. 获取帖子列表
```
GET /api/community/posts
```

**查询参数**
- `category`: 分类 (general/question)
- `status`: 状态 (pending/approved/rejected) - 仅管理员可用
- `page`: 页码
- `per_page`: 每页数量

**响应示例**
```json
{
  "success": true,
  "data": {
    "total": 100,
    "page": 1,
    "per_page": 10,
    "data": [
      {
        "post_id": 1,
        "user_id": 1,
        "nickname": "用户昵称",
        "title": "学习心得分享",
        "content": "我的学习经验...",
        "category": "general",
        "status": "approved",
        "created_at": "2025-09-22T04:55:00",
        "comment_count": 5
      }
    ]
  }
}
```

#### 2. 获取帖子详情
```
GET /api/community/posts/{post_id}
```

#### 3. 创建帖子
```
POST /api/community/posts
```

**请求参数**
```json
{
  "title": "帖子标题",
  "content": "帖子内容",
  "category": "general"  // general/question
}
```

#### 4. 获取帖子评论
```
GET /api/community/posts/{post_id}/comments
```

#### 5. 创建评论
```
POST /api/community/posts/{post_id}/comments
```

**请求参数**
```json
{
  "content": "评论内容"
}
```

#### 6. 删除帖子
```
DELETE /api/community/posts/{post_id}
```

#### 7. 删除评论
```
DELETE /api/community/comments/{comment_id}
```

---

### 管理员功能

#### 1. 获取所有用户
```
GET /api/admin/users
```

**查询参数**
- `page`: 页码
- `per_page`: 每页数量

#### 2. 更新用户角色
```
PUT /api/admin/users/{user_id}/role
```

**请求参数**
```json
{
  "role": "admin"  // student/admin
}
```

#### 3. 获取待审核帖子
```
GET /api/admin/posts/pending
```

#### 4. 审核帖子
```
PUT /api/admin/posts/{post_id}/review
```

**请求参数**
```json
{
  "status": "approved"  // approved/rejected
}
```

#### 5. 添加词汇
```
POST /api/admin/vocab
```

**请求参数**
```json
{
  "word": "example",
  "meaning": "例子",
  "example": "This is an example.",
  "level": "A1"
}
```

#### 6. 更新词汇
```
PUT /api/admin/vocab/{word_id}
```

#### 7. 删除词汇
```
DELETE /api/admin/vocab/{word_id}
```

#### 8. 添加语法教程
```
POST /api/admin/grammar
```

**请求参数**
```json
{
  "title": "现在时态",
  "content": "现在时态的用法...",
  "level": "A1"
}
```

#### 9. 添加听力材料
```
POST /api/admin/listening
```

**请求参数**
```json
{
  "title": "日常对话",
  "audio_url": "https://example.com/audio.mp3",
  "transcript": "对话内容...",
  "level": "A1"
}
```

#### 10. 创建测验
```
POST /api/admin/quiz
```

**请求参数**
```json
{
  "quiz_type": "vocab",
  "title": "A1词汇测试",
  "total_points": 100
}
```

#### 11. 添加测验题目
```
POST /api/admin/quiz/{quiz_id}/questions
```

**请求参数**
```json
{
  "question": "What does 'hello' mean?",
  "option_a": "你好",
  "option_b": "再见",
  "option_c": "谢谢",
  "option_d": "对不起",
  "correct_opt": "A",
  "score": 10
}
```

#### 12. 获取系统统计
```
GET /api/admin/statistics
```

**响应示例**
```json
{
  "success": true,
  "data": {
    "users": {
      "total_users": 1000,
      "admin_count": 5,
      "student_count": 995
    },
    "vocab_count": 2000,
    "grammar_count": 150,
    "listening_count": 100,
    "quiz_count": 50,
    "quiz_attempts": 5000,
    "posts": {
      "total_posts": 500,
      "pending_posts": 10,
      "approved_posts": 480
    },
    "comment_count": 2000,
    "today_users": 50
  }
}
```

#### 13. 获取测验成绩统计
```
GET /api/admin/statistics/quiz-performance
```

#### 14. 获取用户进度统计
```
GET /api/admin/statistics/user-progress
```

---

### 日志系统

#### 1. 获取我的活动日志
```
GET /api/logs/my-logs
```

**查询参数**
- `page`: 页码
- `per_page`: 每页数量

**响应示例**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "_id": "60f7b1234567890abcdef123",
        "user_id": 1,
        "nickname": "用户昵称",
        "action_type": "quiz_attempt",
        "timestamp": "2025-09-22T04:55:00.607Z",
        "details": {
          "quiz_id": 1,
          "quiz_title": "A1词汇测试",
          "score": 85,
          "accuracy": 85.0
        }
      }
    ],
    "page": 1,
    "per_page": 20
  }
}
```

#### 2. 获取用户活动日志（管理员）
```
GET /api/logs/user/{user_id}/logs
```

#### 3. 根据操作类型获取日志（管理员）
```
GET /api/logs/by-action/{action_type}
```

**操作类型包括**
- `user_login` - 用户登录
- `user_logout` - 用户登出
- `quiz_attempt` - 测验尝试
- `learning_progress` - 学习进度
- `post_created` - 帖子创建
- `comment_created` - 评论创建
- `admin_action` - 管理员操作

#### 4. 根据日期范围获取日志（管理员）
```
GET /api/logs/by-date-range
```

**查询参数**
- `start_date`: 开始日期 (ISO格式: 2025-09-22 或 2025-09-22T04:55:00)
- `end_date`: 结束日期
- `user_id`: 用户ID（可选）
- `page`: 页码
- `per_page`: 每页数量

#### 5. 获取日志统计（管理员）
```
GET /api/logs/statistics
```

**查询参数**
- `start_date`: 开始日期（可选）
- `end_date`: 结束日期（可选）

**响应示例**
```json
{
  "success": true,
  "data": {
    "total_logs": 10000,
    "today_logs": 150,
    "action_type_stats": [
      {
        "action_type": "user_login",
        "count": 2000,
        "unique_user_count": 500
      },
      {
        "action_type": "quiz_attempt",
        "count": 5000,
        "unique_user_count": 800
      }
    ]
  }
}
```

#### 6. 手动创建日志
```
POST /api/logs/create
```

**请求参数**
```json
{
  "action_type": "custom_action",
  "details": {
    "description": "自定义操作描述",
    "additional_info": "额外信息"
  }
}
```

#### 7. 记录测验尝试日志
```
POST /api/logs/log-quiz-attempt
```

**请求参数**
```json
{
  "quiz_id": 1,
  "quiz_title": "测验标题",
  "score": 85,
  "accuracy": 85.0
}
```

#### 8. 记录学习进度日志
```
POST /api/logs/log-learning-progress
```

**请求参数**
```json
{
  "content_type": "vocab",
  "content_id": 123,
  "action": "completed"
}
```

#### 9. 获取最近活动
```
GET /api/logs/recent-activities
```

**查询参数**
- `limit`: 限制数量，最多50条

---

## Flutter开发注意事项

### 1. HTTP客户端配置
```dart
import 'package:dio/dio.dart';

class ApiClient {
  static const String baseUrl = 'http://localhost:5000/api';
  late Dio _dio;

  ApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: Duration(seconds: 5),
      receiveTimeout: Duration(seconds: 3),
    ));

    // 添加请求拦截器，自动添加Token
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        String? token = getStoredToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
    ));
  }
}
```

### 2. Token管理
```dart
import 'package:shared_preferences/shared_preferences.dart';

class TokenManager {
  static const String _tokenKey = 'jwt_token';

  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }
}
```

### 3. 响应模型示例
```dart
class ApiResponse<T> {
  final bool success;
  final String message;
  final T? data;

  ApiResponse({
    required this.success,
    required this.message,
    this.data,
  });

  factory ApiResponse.fromJson(Map<String, dynamic> json, T Function(dynamic)? fromJsonT) {
    return ApiResponse<T>(
      success: json['success'],
      message: json['message'],
      data: fromJsonT != null ? fromJsonT(json['data']) : json['data'],
    );
  }
}

class User {
  final int userId;
  final String email;
  final String nickname;
  final String role;

  User({
    required this.userId,
    required this.email,
    required this.nickname,
    required this.role,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      userId: json['user_id'],
      email: json['email'],
      nickname: json['nickname'],
      role: json['role'],
    );
  }
}
```

### 4. 错误处理
```dart
class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException(this.statusCode, this.message);

  @override
  String toString() => 'ApiException: $statusCode - $message';
}

// 使用示例
try {
  final response = await apiClient.post('/auth/login', data: loginData);
  if (response.data['success']) {
    // 登录成功
    String token = response.data['data']['token'];
    await TokenManager.saveToken(token);
  } else {
    throw ApiException(400, response.data['message']);
  }
} on DioException catch (e) {
  if (e.response != null) {
    throw ApiException(e.response!.statusCode!, e.response!.data['message']);
  } else {
    throw ApiException(0, '网络连接失败');
  }
}
```

### 5. 分页处理
```dart
class PaginatedResponse<T> {
  final List<T> data;
  final int total;
  final int page;
  final int perPage;

  PaginatedResponse({
    required this.data,
    required this.total,
    required this.page,
    required this.perPage,
  });

  bool get hasMore => page * perPage < total;
}
```

### 6. 实时更新建议
- 用户学习进度：本地存储 + 定期同步
- 新消息通知：轮询或WebSocket（后期扩展）
- 离线支持：缓存学习材料和用户数据

### 7. 安全考虑
- Token过期自动刷新
- 敏感数据加密存储
- 网络请求HTTPS（生产环境）
- 输入验证和XSS防护

---

## 测试数据

### 测试用户账号
```
邮箱: test@example.com
密码: testpass123
角色: student

邮箱: admin@example.com
密码: adminpass123
角色: admin
```

### 示例测试流程
1. 用户注册/登录
2. 获取学习资源（词汇/语法/听力）
3. 完成测验并查看结果
4. 参与社区讨论
5. 查看学习进度和活动日志

---

## 更新日志

### v1.0.0 (2025-09-22)
- 完成基础用户认证系统
- 实现学习资源管理（词汇、语法、听力）
- 完成测验系统和成绩统计
- 实现社区功能（帖子、评论）
- 完成管理员后台功能
- 集成MongoDB日志系统
- 提供完整的RESTful API

---

## 联系方式

如有技术问题或需要进一步对接，请联系后端开发团队。

**文档最后更新**: 2025年9月22日