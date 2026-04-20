# OPC Platform - 部署指南

## 🚀 部署状态

### 当前状态
- **代码仓库**: https://github.com/MoKangMedical/opc-platform
- **最新提交**: feat: 完整实现OPC平台核心功能
- **部署平台**: Render.com
- **部署配置**: render.yaml

### 自动部署
代码推送到GitHub后，Render.com会自动开始部署流程。

## 📋 部署步骤

### 1. 检查GitHub仓库
访问: https://github.com/MoKangMedical/opc-platform

确认：
- ✅ 代码已推送
- ✅ 所有文件已提交
- ✅ 最新提交显示正常

### 2. 检查Render.com部署

#### 方法1: 通过Render Dashboard
1. 访问: https://dashboard.render.com
2. 使用GitHub账号登录
3. 查看服务列表中的 `opc-platform`
4. 检查部署状态和日志

#### 方法2: 通过部署URL
部署完成后，访问: https://opc-platform.onrender.com

### 3. 部署状态说明

#### 部署中 (In Progress)
- 构建日志会显示安装依赖过程
- 通常需要3-5分钟

#### 部署成功 (Live)
- 状态显示为 "Live"
- 可以访问服务URL
- 健康检查端点正常: /api/health

#### 部署失败 (Failed)
- 查看构建日志中的错误信息
- 常见问题：
  - 依赖安装失败
  - 数据库连接问题
  - 环境变量配置错误

## 🔧 环境配置

### 必需的环境变量
Render.com会自动配置以下环境变量：

```yaml
PYTHON_VERSION: "3.12.0"
DATABASE_URL: <从数据库自动获取>
```

### 数据库配置
- **数据库名称**: opc_platform
- **计划**: Free
- **连接**: 自动配置

## 🧪 部署后测试

### 1. 健康检查
```bash
curl https://opc-platform.onrender.com/api/health
```

预期响应：
```json
{
  "status": "healthy",
  "platform": "OPC Platform",
  "version": "3.0.0"
}
```

### 2. API测试
```bash
# 测试用户注册
curl -X POST https://opc-platform.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"test123456"}'

# 测试项目列表
curl https://opc-platform.onrender.com/api/projects
```

### 3. 前端测试
访问: https://opc-platform.onrender.com

检查：
- ✅ 首页加载正常
- ✅ 导航菜单工作
- ✅ 登录/注册页面可用
- ✅ 移动端显示正常

## 📊 监控和日志

### 查看日志
1. 登录Render Dashboard
2. 选择 `opc-platform` 服务
3. 点击 "Logs" 标签
4. 查看实时日志

### 监控指标
- **CPU使用率**: 正常 < 50%
- **内存使用**: 正常 < 512MB
- **响应时间**: 正常 < 500ms
- **错误率**: 正常 < 1%

## 🔄 更新部署

### 自动更新
每次推送到GitHub main分支，Render.com会自动重新部署。

### 手动更新
1. 登录Render Dashboard
2. 选择 `opc-platform` 服务
3. 点击 "Manual Deploy"
4. 选择 "Deploy latest commit"

## 🛠️ 故障排除

### 问题1: 部署失败
**解决方案**:
1. 检查requirements.txt中的依赖版本
2. 查看构建日志中的错误信息
3. 确保Python版本兼容

### 问题2: 数据库连接失败
**解决方案**:
1. 检查DATABASE_URL环境变量
2. 确保数据库服务已创建
3. 检查数据库连接字符串格式

### 问题3: 服务无法访问
**解决方案**:
1. 检查服务状态是否为"Live"
2. 查看服务日志中的错误
3. 检查健康检查端点

### 问题4: 性能问题
**解决方案**:
1. 升级到付费计划
2. 优化数据库查询
3. 添加缓存层

## 📈 性能优化

### 免费计划限制
- **CPU**: 0.1 CPU
- **内存**: 512MB
- **带宽**: 100GB/月
- **休眠**: 15分钟无请求后休眠

### 优化建议
1. **数据库优化**
   - 添加索引
   - 优化查询
   - 使用连接池

2. **缓存策略**
   - 添加Redis缓存
   - 静态资源CDN
   - API响应缓存

3. **代码优化**
   - 异步处理
   - 批量操作
   - 减少数据库查询

## 🔐 安全配置

### 生产环境安全
1. **环境变量**
   - 不要在代码中硬编码密钥
   - 使用Render的环境变量功能

2. **数据库安全**
   - 使用强密码
   - 限制数据库访问IP
   - 定期备份

3. **API安全**
   - 启用HTTPS
   - 配置CORS
   - 限制请求频率

## 📞 技术支持

### Render.com支持
- 文档: https://render.com/docs
- 社区: https://community.render.com
- 状态: https://status.render.com

### 项目支持
- GitHub Issues: https://github.com/MoKangMedical/opc-platform/issues
- 项目文档: README.md

---

## ✅ 部署检查清单

- [ ] 代码已推送到GitHub
- [ ] Render.com服务已创建
- [ ] 数据库已配置
- [ ] 环境变量已设置
- [ ] 部署成功完成
- [ ] 健康检查通过
- [ ] API测试通过
- [ ] 前端页面正常
- [ ] 移动端显示正常
- [ ] 监控已配置

---

**部署完成后，请更新DNS配置和域名绑定（如需要）**

**最后更新**: 2026-04-20
