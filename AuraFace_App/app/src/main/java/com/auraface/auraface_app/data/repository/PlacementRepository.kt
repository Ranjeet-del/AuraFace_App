package com.auraface.auraface_app.data.repository

import com.auraface.auraface_app.data.network.api.PlacementApi
import com.auraface.auraface_app.data.remote.dto.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.asRequestBody
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PlacementRepository @Inject constructor(
    private val api: PlacementApi
) {
    suspend fun getReadinessProfile() = api.getReadinessProfile()

    suspend fun addSkill(name: String, proficiency: String, documentUrl: String? = null) = 
        api.addSkill(mapOf("skill_name" to name, "proficiency" to proficiency, "document_url" to (documentUrl ?: "")))
    
    suspend fun addCertification(name: String, issuer: String, credentialUrl: String? = null) =
        api.addCertification(
            mapOf(
                "name" to name, 
                "issuing_org" to issuer, 
                "credential_url" to (credentialUrl ?: "")
            )
        )

    suspend fun addProject(title: String, description: String, techStack: String, documentUrl: String? = null) =
        api.addProject(mapOf("title" to title, "description" to description, "tech_stack" to techStack, "document_url" to (documentUrl ?: "")))
    
    suspend fun addInternship(company: String, role: String, startDate: String, documentUrl: String? = null) =
        api.addInternship(mapOf("company_name" to company, "role" to role, "start_date" to startDate, "document_url" to (documentUrl ?: "")))
        
    suspend fun addEvent(name: String, type: String, date: String, documentUrl: String? = null) =
        api.addEvent(mapOf("event_name" to name, "event_type" to type, "date" to date, "document_url" to (documentUrl ?: "")))

    suspend fun uploadDocument(file: java.io.File): String? {
        return try {
             val requestFile = file.asRequestBody("multipart/form-data".toMediaTypeOrNull())
             val body = okhttp3.MultipartBody.Part.createFormData("file", file.name, requestFile)
             api.uploadDocument(body).url
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}
