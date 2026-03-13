package com.auraface.auraface_app.presentation.placement

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.auraface.auraface_app.data.repository.PlacementRepository
import com.auraface.auraface_app.data.remote.dto.StudentReadinessDto
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class PlacementViewModel @Inject constructor(
    private val repository: PlacementRepository
) : ViewModel() {

    private val _state = MutableStateFlow<PlacementState>(PlacementState.Loading)
    val state = _state.asStateFlow()

    init {
        loadData()
    }

    fun loadData() {
        viewModelScope.launch {
            _state.value = PlacementState.Loading
            try {
                val data = repository.getReadinessProfile()
                _state.value = PlacementState.Success(data)
            } catch (e: Exception) {
                _state.value = PlacementState.Error(e.message ?: "Unknown error")
            }
        }
    }
    
    fun addSkill(name: String, level: String, file: java.io.File? = null) {
        viewModelScope.launch {
            try {
                var url: String? = null
                if (file != null) {
                    url = repository.uploadDocument(file)
                }
                repository.addSkill(name, level, url)
                loadData() // Refresh
            } catch (e: Exception) {
                // handle error
            }
        }
    }

    fun addProject(title: String, description: String, techStack: String, file: java.io.File? = null) {
        viewModelScope.launch {
            try {
                var url: String? = null
                if (file != null) {
                    url = repository.uploadDocument(file)
                }
                repository.addProject(title, description, techStack, url)
                loadData()
            } catch (e: Exception) {
                // handle error
            }
        }
    }
    
    fun addCertification(name: String, issuer: String, file: java.io.File? = null) {
        viewModelScope.launch {
            try {
                var url: String? = null
                if (file != null) {
                    url = repository.uploadDocument(file)
                }
                repository.addCertification(name, issuer, url)
                loadData()
            } catch (e: Exception) {
                // handle error
            }
        }
    }
    
    fun addInternship(company: String, role: String, startDate: String, file: java.io.File? = null) {
        viewModelScope.launch {
            try {
                var url: String? = null
                if (file != null) {
                    url = repository.uploadDocument(file)
                }
                repository.addInternship(company, role, startDate, url)
                loadData()
            } catch (e: Exception) {
                // handle error
            }
        }
    }
    
    fun addEvent(name: String, type: String, date: String, file: java.io.File? = null) {
        viewModelScope.launch {
             try {
                 var url: String? = null
                 if (file != null) {
                     url = repository.uploadDocument(file)
                 }
                 repository.addEvent(name, type, date, url)
                 loadData()
             } catch (e: Exception) {
                 // handle error
             }
         }
    }
}

sealed class PlacementState {
    object Loading : PlacementState()
    data class Success(val data: StudentReadinessDto) : PlacementState()
    data class Error(val message: String) : PlacementState()
}
