package com.auraface.auraface_app.presentation.student

import androidx.compose.runtime.*
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.auraface.auraface_app.data.repository.AuthRepository
import com.auraface.auraface_app.data.repository.StudentRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

import com.auraface.auraface_app.data.network.model.TimetableItem
import com.auraface.auraface_app.data.network.model.GamificationProfile
import com.auraface.auraface_app.data.repository.QuizRepository

@HiltViewModel
class StudentViewModel @Inject constructor(
    private val repo: StudentRepository,
    private val authRepo: AuthRepository,
    private val quizRepo: QuizRepository
) : ViewModel() {

    var analytics by mutableStateOf<com.auraface.auraface_app.data.network.model.StudentAnalytics?>(null)
        private set

    var profile by mutableStateOf<com.auraface.auraface_app.data.remote.dto.UserProfile?>(null)
        private set

    var attendanceRecords by mutableStateOf<List<com.auraface.auraface_app.domain.model.Attendance>>(emptyList())
        private set

    var leaveRequests by mutableStateOf<List<Map<String, Any>>>(emptyList())
        private set

    var timetable by mutableStateOf<List<TimetableItem>>(emptyList())
        private set

    var nextClass by mutableStateOf<TimetableItem?>(null)
        private set

    var gamificationProfile by mutableStateOf<GamificationProfile?>(null)
        private set

    var error by mutableStateOf<String?>(null)
        private set

    init {
        loadAnalytics()
        loadProfile()
        loadAttendanceHistory()
        loadLeaves()
        loadTimetable()
        loadGamificationProfile()
        // loadNextClass()
    }

    private fun loadNextClass() {
        viewModelScope.launch {
            // try { nextClass = repo.getNextClass() } catch(e: Exception) {}
        }
    }

    private fun loadAnalytics() {
        // Will be dynamically calculated after attendance is loaded to show REAL DB numbers
    }

    private fun calculateDynamicAnalytics() {
        if (attendanceRecords.isEmpty()) return
        
        // Ignore "NC" (Not Conducted) records from the total class calculation if needed, 
        // but NC isn't actually returned as a status if it wasn't conducted. It's only NC in the frontend table.
        // Actually, backend returns "NC" status for entirely unconducted subjects perfectly.
        val validRecords = attendanceRecords.filter { it.status != "NC" }
        
        val total = validRecords.size
        val present = validRecords.count { it.status.equals("Present", ignoreCase = true) || it.status.equals("Late", ignoreCase = true) }
        val overallPct = if (total > 0) (present.toFloat() / total.toFloat()) * 100f else 0f

        val subjectGroups = validRecords.groupBy { it.subject ?: "Unknown" }.filterKeys { it != "Unknown" }
        val subjAttendanceList = subjectGroups.map { (subj, records) ->
            val totalSubj = records.size
            val presentSubj = records.count { it.status.equals("Present", ignoreCase = true) || it.status.equals("Late", ignoreCase = true) }
            val pct = if (totalSubj > 0) (presentSubj.toFloat() / totalSubj.toFloat()) * 100f else 0f
            com.auraface.auraface_app.data.network.model.SubjectAttendance(
                subjectName = subj,
                attendedClasses = presentSubj,
                totalClasses = totalSubj,
                percentage = kotlin.math.round(pct * 10) / 10f
            )
        }

        analytics = com.auraface.auraface_app.data.network.model.StudentAnalytics(
            overallAttendance = kotlin.math.round(overallPct * 10) / 10f,
            subjectWiseAttendance = subjAttendanceList,
            recentAttendance = emptyList() // or dynamic chart parsing
        )
    }

    fun loadProfile() {
        viewModelScope.launch {
            try { 
                error = null
                profile = authRepo.getProfile() 
            } catch(e: Exception) {
                error = "Failed to load profile: ${e.message}"
                e.printStackTrace()
            }
        }
    }

    fun loadAttendanceHistory() {
        viewModelScope.launch {
            try { 
                attendanceRecords = repo.getMyAttendance() 
                calculateDynamicAnalytics()
            } catch(e: Exception) {
                android.util.Log.e("StudentViewModel", "Error loading attendance", e)
            }
        }
    }

    fun loadLeaves() {
        viewModelScope.launch {
            try { 
                leaveRequests = repo.getMyLeaves() 
            } catch(e: Exception) {
                android.util.Log.e("StudentViewModel", "Error loading leaves", e)
            }
        }
    }

    fun loadGamificationProfile() {
        viewModelScope.launch {
            try {
                val response = quizRepo.getProfile()
                if (response.isSuccessful) {
                    gamificationProfile = response.body()
                }
            } catch (e: Exception) {
                android.util.Log.e("StudentViewModel", "Error loading gamification profile", e)
            }
        }
    }

    fun loadTimetable() {
        viewModelScope.launch {
            try { timetable = repo.getTimetable() } catch(e: Exception) {}
        }
    }

    fun submitLeave(reason: String, onSuccess: () -> Unit) {
        viewModelScope.launch {
            try {
                repo.submitLeave(reason)
                loadLeaves()
                onSuccess()
            } catch(e: Exception) {
                android.util.Log.e("StudentViewModel", "Error submitting leave", e)
            }
        }
    }

    fun updateBloodGroup(bloodGroup: String, onSuccess: () -> Unit, onError: (String) -> Unit) {
        viewModelScope.launch {
            try {
                repo.updateBloodGroup(bloodGroup)
                loadProfile()
                onSuccess()
            } catch(e: Exception) {
                e.printStackTrace()
                onError(e.message ?: "Failed to update blood group")
            }
        }
    }

    fun changePassword(newPassword: String, onSuccess: () -> Unit, onError: (String) -> Unit) {
        viewModelScope.launch {
            // try {
            //     repo.changePassword(newPassword)
            //     onSuccess()
            // } catch(e: Exception) {
            //     onError(e.message ?: "Failed to update password")
            // }
        }
    }

    // --- Academic ---
    var examSchedule by mutableStateOf<List<com.auraface.auraface_app.data.network.api.ExamScheduleDTO>>(emptyList())
        private set
    var results by mutableStateOf<List<com.auraface.auraface_app.data.network.api.ResultDTO>>(emptyList())
        private set
    var cgpa by mutableStateOf<com.auraface.auraface_app.data.network.api.GpaDTO?>(null)
        private set

    fun loadExamSchedule() { viewModelScope.launch { examSchedule = repo.getExamSchedule() } }
    fun loadResults() { viewModelScope.launch { results = repo.getMyResults() } }
    fun loadCGPA() { viewModelScope.launch { cgpa = repo.getMyCGPA() } }

    var notifications by mutableStateOf<List<com.auraface.auraface_app.data.network.model.Notification>>(emptyList())
        private set

    fun loadNotifications() {
        viewModelScope.launch {
            try {
                notifications = repo.getNotifications()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    var proctorMeetings by mutableStateOf<List<com.auraface.auraface_app.data.network.model.ProctorMeeting>>(emptyList())
        private set

    fun loadProctorMeetings() {
        viewModelScope.launch {
            try { proctorMeetings = repo.getMyProctorMeetings() } catch(e: Exception){}
        }
    }

    fun sendMessageToClassTeacher(message: String, onSuccess: () -> Unit) {
        viewModelScope.launch {
            try {
                repo.sendMessageToClassTeacher(message)
                onSuccess()
            } catch(e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun respondToProctorMeeting(id: Int, response: String, onSuccess: () -> Unit) {
        viewModelScope.launch {
            try {
                repo.respondToProctorMeeting(id, response)
                onSuccess()
                loadProctorMeetings() // Reload to show update
            } catch(e: Exception) {
                e.printStackTrace()
            }
        }
    }

    var teacherAvailability by mutableStateOf<List<com.auraface.auraface_app.data.network.api.TeacherAvailabilityDTO>>(emptyList())
        private set

    var academicCalendar by mutableStateOf<List<com.auraface.auraface_app.data.network.api.CalendarEventDTO>>(emptyList())
        private set

    fun loadTeacherAvailability() {
        viewModelScope.launch {
            try { teacherAvailability = repo.getTeacherAvailability() } catch(e: Exception){}
        }
    }

    fun loadAcademicCalendar() {
        viewModelScope.launch {
            try { academicCalendar = repo.getAcademicCalendar() } catch(e: Exception){}
        }
    }
}
