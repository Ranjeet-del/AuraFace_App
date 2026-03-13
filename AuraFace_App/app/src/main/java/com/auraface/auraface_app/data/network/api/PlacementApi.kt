package com.auraface.auraface_app.data.network.api

import com.auraface.auraface_app.data.remote.dto.*
import retrofit2.http.*

interface PlacementApi {

    @GET("placement/profile")
    suspend fun getReadinessProfile(): StudentReadinessDto

    @POST("placement/skill")
    suspend fun addSkill(@Body skill: Map<String, String>): PlacementSkillDto

    @POST("placement/certification")
    suspend fun addCertification(@Body cert: Map<String, String>): PlacementCertificationDto

    @POST("placement/internship")
    suspend fun addInternship(@Body intern: Map<String, Any>): PlacementInternshipDto

    @POST("placement/project")
    suspend fun addProject(@Body project: Map<String, String>): PlacementProjectDto

    @POST("placement/event")
    suspend fun addEvent(@Body event: Map<String, String>): PlacementEventDto
    
    @Multipart
    @POST("placement/upload")
    suspend fun uploadDocument(
        @Part file: okhttp3.MultipartBody.Part
    ): ChatUploadResponse // Reusing this DTO since it has url/filename
}
