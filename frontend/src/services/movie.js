import api, { get, post, put, del } from './api'

/**
 * 电影生成相关服务
 * 遵循项目架构：所有API调用通过service层，composables不直接使用api
 */
export const movieService = {
    // ==================== 角色管理 ====================

    /**
     * 获取项目的角色列表
     */
    getCharacters(projectId) {
        return get(`/movie/projects/${projectId}/characters`)
    },

    /**
     * 从章节提取角色
     */
    extractCharacters(chapterId, data) {
        return post(`/movie/chapters/${chapterId}/extract-characters`, data)
    },

    /**
     * 生成角色形象
     */
    generateCharacterAvatar(characterId, data) {
        const formData = new FormData()
        formData.append('api_key_id', data.api_key_id)
        if (data.model) formData.append('model', data.model)
        if (data.prompt) formData.append('prompt', data.prompt)
        if (data.style) formData.append('style', data.style)

        // 发送选中的参考图索引（逗号分隔）
        if (data.selected_reference_indices && data.selected_reference_indices.length > 0) {
            formData.append('selected_reference_indices', data.selected_reference_indices.join(','))
        }

        return api.post(`/movie/characters/${characterId}/generate`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    /**
     * 批量生成角色定妆照
     */
    batchGenerateAvatars(projectId, data) {
        return post(`/movie/projects/${projectId}/characters/batch-generate`, data)
    },

    /**
     * 删除角色
     */
    deleteCharacter(characterId) {
        return api.delete(`/movie/characters/${characterId}`)
    },

    // ==================== 场景管理 ====================

    /**
     * 获取章节关联的剧本详情
     */
    getScript(chapterId) {
        return get(`/movie/chapters/${chapterId}/script`)
    },

    /**
     * 从章节提取场景（新架构）
     */
    extractScenes(chapterId, data) {
        return post(`/movie/chapters/${chapterId}/scenes`, data)
    },

    /**
     * 批量生成场景图
     */
    batchGenerateSceneImages(scriptId, data) {
        return post(`/movie/scripts/${scriptId}/scene-images`, data)
    },

    /**
     * 生成单个场景图
     */
    generateSceneImage(sceneId, data) {
        return post(`/movie/scenes/${sceneId}/scene-image`, data)
    },

    /**
     * 重新生成场景图
     */
    regenerateSceneImage(sceneId, data) {
        return post(`/movie/scenes/${sceneId}/regenerate-scene-image`, data)
    },

    // ==================== 分镜管理 ====================

    /**
     * 从剧本提取分镜
     */
    extractShots(scriptId, data) {
        return post(`/movie/scripts/${scriptId}/extract-shots`, data)
    },

    /**
     * 从单个场景重新提取分镜
     */
    extractSingleSceneShots(sceneId, data) {
        return post(`/movie/scenes/${sceneId}/extract-shots`, data)
    },

    /**
     * 更新分镜信息
     */
    updateShot(shotId, data) {
        return put(`/movie/shots/${shotId}`, data)
    },

    /**
     * 删除分镜
     */
    deleteShot(shotId) {
        return del(`/movie/shots/${shotId}`)
    },

    /**
     * 更新分镜顺序
     */
    updateShotOrder(shotId, orderIndex) {
        return put(`/movie/shots/${shotId}/order`, { order_index: orderIndex })
    },

    /**
     * 获取章节的所有分镜
     */
    getShotsByChapter(chapterId) {
        return get(`/movie/shots/by-chapter/${chapterId}`)
    },


    // ==================== 关键帧管理 ====================

    /**
     * 为单个分镜生成关键帧
     */
    generateSingleKeyframe(shotId, data) {
        return post(`/movie/shots/${shotId}/generate-keyframe`, data)
    },

    /**
     * 为剧本批量生成分镜关键帧
     */
    generateKeyframes(scriptId, data) {
        return post(`/movie/scripts/${scriptId}/generate-keyframes`, data)
    },

    // ==================== 过渡视频管理 ====================

    /**
     * 创建过渡视频记录
     */
    createTransitions(scriptId, data) {
        return post(`/movie/scripts/${scriptId}/create-transitions`, data)
    },

    /**
     * 批量生成过渡视频
     */
    generateTransitionVideos(scriptId, data) {
        return post(`/movie/scripts/${scriptId}/generate-transition-videos`, data)
    },

    /**
     * 生成单个过渡视频
     */
    generateSingleTransition(transitionId, data) {
        return post(`/movie/transitions/${transitionId}/generate-video`, data)
    },

    /**
     * 获取剧本的过渡列表
     */
    getTransitions(scriptId) {
        return get(`/movie/scripts/${scriptId}/transitions`)
    },

    /**
     * 获取单个过渡
     */
    getTransition(transitionId) {
        return get(`/movie/transitions/${transitionId}`)
    },

    /**
     * 更新过渡提示词
     */
    updateTransitionPrompt(transitionId, prompt) {
        return put(`/movie/transitions/${transitionId}`, { video_prompt: prompt })
    },

    /**
     * 删除过渡
     */
    deleteTransition(transitionId) {
        return del(`/movie/transitions/${transitionId}`)
    },

    // ==================== 参考图管理 ====================

    /**
     * 上传角色参考图
     */
    uploadReferenceImage(characterId, file) {
        const formData = new FormData()
        formData.append('file', file)

        return api.post(`/movie/characters/${characterId}/reference-images`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    /**
     * 删除角色参考图
     */
    deleteReferenceImage(characterId, imageIndex) {
        return del(`/movie/characters/${characterId}/reference-images/${imageIndex}`)
    },

    // ==================== 道具管理 ====================

    getProps(projectId) {
        return get(`/movie/projects/${projectId}/props`)
    },

    extractProps(chapterId, data) {
        return post(`/movie/chapters/${chapterId}/extract-props`, data)
    },

    generatePropImage(propId, data) {
        const formData = new FormData()
        formData.append('api_key_id', data.api_key_id)
        if (data.model) formData.append('model', data.model)
        if (data.prompt) formData.append('prompt', data.prompt)
        if (data.style) formData.append('style', data.style)

        return api.post(`/movie/props/${propId}/generate`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    batchGeneratePropImages(projectId, data) {
        return post(`/movie/projects/${projectId}/props/batch-generate`, data)
    },

    updateProp(propId, data) {
        return put(`/movie/props/${propId}`, data)
    },

    deleteProp(propId) {
        return del(`/movie/props/${propId}`)
    },

    uploadPropReferenceImage(propId, file) {
        const formData = new FormData()
        formData.append('file', file)

        return api.post(`/movie/props/${propId}/reference-images`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    deletePropReferenceImage(propId, imageIndex) {
        return del(`/movie/props/${propId}/reference-images/${imageIndex}`)
    }
}

export default movieService
