<template>
  <div class="not-found">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>页面未找到</h2>
      <p>抱歉，您访问的页面不存在</p>
      <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f5f7fa;
}

.not-found-content {
  text-align: center;
}

.not-found-content h1 {
  font-size: 120px;
  color: #409eff;
  margin: 0;
  line-height: 1;
}

.not-found-content h2 {
  font-size: 24px;
  color: #303133;
  margin: 16px 0 8px;
}

.not-found-content p {
  font-size: 16px;
  color: #909399;
  margin-bottom: 32px;
}
</style>
