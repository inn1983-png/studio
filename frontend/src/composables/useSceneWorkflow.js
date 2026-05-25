import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import movieService from '@/services/movie'
import { useTaskPoller } from './useTaskPoller'

export function useSceneWorkflow() {
    const { startPolling: startTaskPolling, stopPolling: stopTaskPolling } = useTaskPoller()
    onUnmounted(() => { stopTaskPolling() })

    const script = ref(null)
    const extracting = ref(false)
    const generatingSceneImages = ref(new Set())
    const batchGenerating = ref(false)

    const loadScript = async (chapterId) => {
        if (!chapterId) return
        try {
            const response = await movieService.getScript(chapterId)
            script.value = response
        } catch (error) {
            console.error('Failed to load script:', error)
            script.value = null
        }
    }

    const extractScenes = async (chapterId, apiKeyId, model) => {
        extracting.value = true
        try {
            const response = await movieService.extractScenes(chapterId, {
                api_key_id: apiKeyId,
                model
            })

            if (response.task_id) {
                ElMessage.success('场景提取任务已提交')
                startTaskPolling(response.task_id, async () => {
                    ElMessage.success('场景提取完成')
                    await loadScript(chapterId)
                    extracting.value = false
                }, (error) => {
                    ElMessage.error(`提取失败: ${error.message}`)
                    extracting.value = false
                })
            }
        } catch (error) {
            ElMessage.error('场景提取失败')
            extracting.value = false
        }
    }

    const generateSceneImages = async (scriptId, apiKeyId, model, loadScriptFn) => {
        batchGenerating.value = true
        try {
            const response = await movieService.batchGenerateSceneImages(scriptId, {
                api_key_id: apiKeyId,
                model
            })

            if (response.task_id) {
                ElMessage.success('场景图批量生成任务已提交')
                startTaskPolling(response.task_id, async () => {
                    ElMessage.success('场景图批量生成完成')
                    batchGenerating.value = false
                    if (script.value?.chapter_id && loadScriptFn) {
                        await loadScriptFn(script.value.chapter_id, true)
                    }
                }, (error) => {
                    ElMessage.error(`场景图生成失败: ${error.message}`)
                    batchGenerating.value = false
                })
            } else {
                batchGenerating.value = false
            }
        } catch (error) {
            ElMessage.error('场景图生成失败')
            batchGenerating.value = false
        }
    }

    const generateSingleSceneImage = async (sceneId, apiKeyId, model, prompt) => {
        generatingSceneImages.value.add(sceneId)
        try {
            const response = await movieService.generateSceneImage(sceneId, {
                api_key_id: apiKeyId,
                model,
                prompt
            })

            if (response.task_id) {
                ElMessage.success('场景图生成任务已提交')
                startTaskPolling(response.task_id, async () => {
                    ElMessage.success('场景图生成完成')
                    generatingSceneImages.value.delete(sceneId)
                    if (script.value?.chapter_id) {
                        await loadScript(script.value.chapter_id)
                    }
                }, (error) => {
                    ElMessage.error(`场景图生成失败: ${error.message}`)
                    generatingSceneImages.value.delete(sceneId)
                })
            }
        } catch (error) {
            ElMessage.error('场景图生成失败')
            generatingSceneImages.value.delete(sceneId)
        }
    }

    return {
        script,
        extracting,
        generatingSceneImages,
        batchGenerating,
        loadScript,
        extractScenes,
        generateSceneImages,
        generateSingleSceneImage
    }
}
