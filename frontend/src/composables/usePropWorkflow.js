import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import movieService from '@/services/movie'
import { useTaskPoller } from './useTaskPoller'

export function usePropWorkflow(projectId) {
    const { startPolling: startTaskPolling, stopPolling: stopTaskPolling } = useTaskPoller()
    onUnmounted(() => { stopTaskPolling() })

    const props = ref([])
    const extracting = ref(false)
    const generatingIds = ref(new Set())
    const batchGenerating = ref(false)

    const loadProps = async () => {
        if (!projectId.value) return
        try {
            const response = await movieService.getProps(projectId.value)
            props.value = response.props || []
        } catch (error) {
            console.error('Failed to load props:', error)
        }
    }

    const extractProps = async (chapterId, apiKeyId, model) => {
        extracting.value = true
        try {
            const response = await movieService.extractProps(chapterId, {
                api_key_id: apiKeyId,
                model
            })

            if (response.task_id) {
                ElMessage.success('道具提取任务已提交')
                startTaskPolling(response.task_id, async () => {
                    ElMessage.success('道具提取完成')
                    await loadProps()
                    extracting.value = false
                }, (error) => {
                    ElMessage.error(`提取失败: ${error.message}`)
                    extracting.value = false
                })
            }
        } catch (error) {
            ElMessage.error('道具提取失败')
            extracting.value = false
        }
    }

    const generateImage = async (propId, apiKeyId, model, prompt, style) => {
        generatingIds.value.add(propId)
        try {
            const response = await movieService.generatePropImage(propId, {
                api_key_id: apiKeyId,
                model,
                prompt,
                style
            })

            if (response.task_id) {
                ElMessage.success('道具图生成任务已提交')
                startTaskPolling(response.task_id, async () => {
                    ElMessage.success('道具图生成成功')
                    await loadProps()
                    generatingIds.value.delete(propId)
                }, (error) => {
                    ElMessage.error(`生成失败: ${error.message}`)
                    generatingIds.value.delete(propId)
                })
            }
        } catch (error) {
            ElMessage.error('无法启动道具图生成')
            generatingIds.value.delete(propId)
        }
    }

    const batchGenerateImages = async (apiKeyId, model) => {
        batchGenerating.value = true
        try {
            const response = await movieService.batchGeneratePropImages(projectId.value, {
                api_key_id: apiKeyId,
                model
            })

            if (response.task_id) {
                ElMessage.success('批量生成任务已提交')
                startTaskPolling(response.task_id, async (result) => {
                    ElMessage.success(`批量生成完成: 成功 ${result.success}, 失败 ${result.failed}`)
                    await loadProps()
                    batchGenerating.value = false
                }, (error) => {
                    ElMessage.error(`批量生成失败: ${error.message}`)
                    batchGenerating.value = false
                })
            } else {
                batchGenerating.value = false
            }
        } catch (error) {
            ElMessage.error('无法启动批量生成')
            batchGenerating.value = false
        }
    }

    const deleteProp = async (propId) => {
        try {
            await movieService.deleteProp(propId)
            ElMessage.success('道具已删除')
            await loadProps()
        } catch (error) {
            ElMessage.error('删除道具失败')
        }
    }

    return {
        props,
        extracting,
        generatingIds,
        batchGenerating,
        loadProps,
        extractProps,
        generateImage,
        batchGenerateImages,
        deleteProp
    }
}
