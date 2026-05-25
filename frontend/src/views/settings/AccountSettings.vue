<template>
  <div class="setting-section">
    <h2>账户安全</h2>
    <p>保护您的账户安全</p>

    <div class="security-sections">
      <div class="security-card">
        <div class="card-header">
          <div class="card-icon">
            <el-icon><Lock /></el-icon>
          </div>
          <div class="card-content">
            <h3>修改密码</h3>
            <p>定期更改密码以保护账户安全</p>
          </div>
        </div>
        <el-button
          type="primary"
          @click="showPasswordDialog = true"
        >
          修改密码
        </el-button>
      </div>

      <div class="security-card">
        <div class="card-header">
          <div class="card-icon shield">
            <el-icon><Key /></el-icon>
          </div>
          <div class="card-content">
            <h3>账户状态</h3>
            <p>
              <el-tag
                type="success"
                size="small"
              >
                安全
              </el-tag>
              上次登录：{{ formatDate(authStore.user?.last_login, {}, userTimezone) }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      width="520px"
      :close-on-click-modal="false"
      class="password-dialog"
      :show-close="true"
    >
      <template #header>
        <div class="password-dialog-header compact">
          <div class="dialog-icon">
            <el-icon size="28">
              <Lock />
            </el-icon>
          </div>
          <div class="dialog-title">
            <h3>修改密码</h3>
            <p>设置新的安全密码</p>
          </div>
        </div>
      </template>

      <div class="password-form-container compact">
        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-position="top"
        >
          <div class="form-group compact">
            <el-form-item prop="current">
              <el-input
                v-model="passwordForm.current"
                type="password"
                placeholder="当前密码"
                size="default"
                show-password
                clearable
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </div>

          <div class="form-group compact">
            <el-form-item prop="new">
              <el-input
                v-model="passwordForm.new"
                type="password"
                placeholder="新密码"
                size="default"
                show-password
                clearable
                @input="checkPasswordStrength"
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>

              <!-- 紧凑的密码强度指示器和要求 -->
              <div
                v-if="passwordForm.new"
                class="compact-password-info"
              >
                <!-- 密码强度条 -->
                <div class="compact-strength">
                  <div class="strength-label">
                    <span>强度：</span>
                    <span :class="getPasswordStrengthClass()">{{ getPasswordStrengthText() }}</span>
                  </div>
                  <div class="strength-bar">
                    <div
                      class="strength-fill"
                      :class="getPasswordStrengthClass()"
                      :style="getPasswordStrengthWidth()"
                    />
                  </div>
                </div>

                <!-- 紧凑的密码要求 -->
                <div class="compact-requirements">
                  <div class="requirement-row">
                    <div
                      class="requirement-item"
                      :class="{ 'satisfied': passwordForm.new.length >= 8 }"
                    >
                      <el-icon size="12">
                        <Check v-if="passwordForm.new.length >= 8" /><Close v-else />
                      </el-icon>
                      <span>8位+</span>
                    </div>
                    <div
                      class="requirement-item"
                      :class="{ 'satisfied': /[A-Z]/.test(passwordForm.new) }"
                    >
                      <el-icon size="12">
                        <Check v-if="/[A-Z]/.test(passwordForm.new)" /><Close v-else />
                      </el-icon>
                      <span>大写</span>
                    </div>
                    <div
                      class="requirement-item"
                      :class="{ 'satisfied': /[a-z]/.test(passwordForm.new) }"
                    >
                      <el-icon size="12">
                        <Check v-if="/[a-z]/.test(passwordForm.new)" /><Close v-else />
                      </el-icon>
                      <span>小写</span>
                    </div>
                  </div>
                  <div class="requirement-row">
                    <div
                      class="requirement-item"
                      :class="{ 'satisfied': /\d/.test(passwordForm.new) }"
                    >
                      <el-icon size="12">
                        <Check v-if="/\d/.test(passwordForm.new)" /><Close v-else />
                      </el-icon>
                      <span>数字</span>
                    </div>
                    <div
                      class="requirement-item"
                      :class="{ 'satisfied': hasSpecialCharacter }"
                    >
                      <el-icon size="12">
                        <Check v-if="hasSpecialCharacter" /><Close v-else />
                      </el-icon>
                      <span>特殊字符</span>
                    </div>
                  </div>
                </div>
              </div>
            </el-form-item>
          </div>

          <div class="form-group compact">
            <el-form-item prop="confirm">
              <el-input
                v-model="passwordForm.confirm"
                type="password"
                placeholder="确认新密码"
                size="default"
                show-password
                clearable
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>

              <!-- 紧凑的密码匹配状态 -->
              <div
                v-if="passwordForm.confirm"
                class="compact-match"
              >
                <div
                  class="match-item"
                  :class="{ 'matched': passwordForm.new === passwordForm.confirm }"
                >
                  <el-icon size="14">
                    <Check v-if="passwordForm.new === passwordForm.confirm" /><Close v-else />
                  </el-icon>
                  <span>密码匹配</span>
                </div>
              </div>
            </el-form-item>
          </div>
        </el-form>
      </div>

      <template #footer>
        <div class="password-dialog-footer compact">
          <el-button @click="closePasswordDialog">
            取消
          </el-button>
          <el-button
            type="primary"
            :loading="passwordLoading"
            :disabled="!isFormValid"
            @click="changePassword"
          >
            {{ passwordLoading ? '修改中...' : '确认修改' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Lock, Key, Check, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { formatDate, getUserTimezone } from '@/utils/dateUtils'

const authStore = useAuthStore()
const showPasswordDialog = ref(false)
const passwordLoading = ref(false)
const passwordFormRef = ref(null)
const passwordStrength = ref(0)

// 密码修改表单
const passwordForm = reactive({
  current: '',
  new: '',
  confirm: ''
})

// 用户时区
const userTimezone = computed(() => {
  return getUserTimezone(authStore.user);
})

// 密码验证规则
const passwordRules = {
  current: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少8位', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback()
          return
        }
        if (!/[A-Z]/.test(value)) {
          callback(new Error('密码必须包含大写字母'))
          return
        }
        if (!/[a-z]/.test(value)) {
          callback(new Error('密码必须包含小写字母'))
          return
        }
        if (!/\d/.test(value)) {
          callback(new Error('密码必须包含数字'))
          return
        }
        callback()
      },
      trigger: 'blur'
    }
  ],
  confirm: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new) {
          callback(new Error('两次输入的密码不一致'))
          return
        }
        callback()
      },
      trigger: 'blur'
    }
  ]
}

// 密码强度检查
const checkPasswordStrength = () => {
  let strength = 0
  const password = passwordForm.new

  if (!password) {
    passwordStrength.value = 0
    return
  }

  if (password.length >= 8) strength += 1
  if (password.length >= 12) strength += 1
  if (/[a-z]/.test(password)) strength += 1
  if (/[A-Z]/.test(password)) strength += 1
  if (/\d/.test(password)) strength += 1
  if (/[!@#$%^&*()\-_+=.,?":{}|<>]/.test(password)) strength += 1

  passwordStrength.value = Math.min(strength, 5)
}

const getPasswordStrengthText = () => {
  if (passwordStrength.value <= 2) return '弱'
  if (passwordStrength.value <= 4) return '中等'
  return '强'
}

const getPasswordStrengthClass = () => {
  if (passwordStrength.value <= 2) return 'weak'
  if (passwordStrength.value <= 4) return 'medium'
  return 'strong'
}

const getPasswordStrengthWidth = () => {
  return { width: `${(passwordStrength.value / 5) * 100}%` }
}

const hasSpecialCharacter = computed(() => {
  if (!passwordForm.new) return false
  const specialChars = /[!@#$%^&*()\-_+=.,?":{}|<>]/
  return specialChars.test(passwordForm.new)
})

const isFormValid = computed(() => {
  return passwordForm.current &&
         passwordForm.new &&
         passwordForm.confirm &&
         passwordForm.new === passwordForm.confirm &&
         passwordForm.new.length >= 8 &&
         /[A-Z]/.test(passwordForm.new) &&
         /[a-z]/.test(passwordForm.new) &&
         /\d/.test(passwordForm.new)
})

const closePasswordDialog = () => {
  showPasswordDialog.value = false
  Object.assign(passwordForm, {
    current: '',
    new: '',
    confirm: ''
  })
  passwordStrength.value = 0
}

const changePassword = async () => {
  if (!passwordFormRef.value) return

  try {
    await passwordFormRef.value.validate()
  } catch {
    return
  }

  passwordLoading.value = true
  try {
    await authStore.changePassword({
      current_password: passwordForm.current,
      new_password: passwordForm.new
    })

    showPasswordDialog.value = false
    ElMessage.success('密码修改成功')

    Object.assign(passwordForm, {
      current: '',
      new: '',
      confirm: ''
    })
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败，请检查当前密码是否正确')
  } finally {
    passwordLoading.value = false
  }
}
</script>

<style scoped>
.setting-section {
  animation: fadeIn 0.3s ease-in-out;
}

.setting-section h2 {
  font-size: var(--text-xl);
  font-weight: 600;
  margin-bottom: var(--space-xs);
  color: var(--text-primary);
}

.setting-section > p {
  color: var(--text-secondary);
  margin-bottom: var(--space-xl);
}

.security-sections {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-lg);
}

.security-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: var(--space-lg);
  transition: all var(--transition-base);
}

.security-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  gap: var(--space-md);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-base);
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  font-size: 24px;
}

.card-icon.shield {
  color: var(--success-color);
  background: var(--success-light);
}

.card-content h3 {
  font-size: var(--text-lg);
  font-weight: 600;
  margin: 0 0 var(--space-xs) 0;
  color: var(--text-primary);
}

.card-content p {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* 密码对话框样式 */
.password-dialog-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.dialog-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
}

.dialog-title h3 {
  margin: 0;
  font-size: var(--text-lg);
  color: var(--text-primary);
}

.dialog-title p {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.compact-password-info {
  margin-top: var(--space-sm);
  background: var(--bg-secondary);
  padding: var(--space-sm);
  border-radius: var(--radius-base);
}

.compact-strength {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-sm);
}

.strength-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  min-width: 80px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: var(--gray-200);
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.strength-fill.weak { background-color: var(--danger-color); }
.strength-fill.medium { background-color: var(--warning-color); }
.strength-fill.strong { background-color: var(--success-color); }

.compact-requirements {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.requirement-row {
  display: flex;
  gap: var(--space-md);
}

.requirement-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.requirement-item.satisfied {
  color: var(--success-color);
}

.compact-match {
  margin-top: var(--space-xs);
}

.match-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.match-item.matched {
  color: var(--success-color);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
