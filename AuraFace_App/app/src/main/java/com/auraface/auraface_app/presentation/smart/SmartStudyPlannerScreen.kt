package com.auraface.auraface_app.presentation.smart

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import kotlinx.coroutines.delay

data class StudyTask(
    val title: String,
    val duration: String,
    val reason: String // E.g., "Upcoming Exam", "Low Attendance"
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SmartStudyPlannerScreen(navController: NavController) {
    var isLoading by remember { mutableStateOf(true) }
    var tasksList by remember { mutableStateOf<List<StudyTask>>(emptyList()) }

    LaunchedEffect(Unit) {
        delay(1500) // AI generating schedule
        tasksList = listOf(
            StudyTask("Review Java Fundamentals", "45 mins", "Upcoming Internal Test"),
            StudyTask("Complete OS Assignment", "1 hr", "Deadline Tomorrow"),
            StudyTask("Study Data Structures", "30 mins", "Low Performance in recent quiz"),
            StudyTask("Revise Mathematics", "1 hr", "Missed last 2 classes")
        )
        isLoading = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("AI Study Planner", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { padding ->
        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    CircularProgressIndicator()
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("AI is generating your study schedule...", color = Color.Gray)
                }
            }
        } else {
            Column(
                modifier = Modifier.fillMaxSize().padding(padding)
            ) {
                Text(
                    "Your Personalized Plan",
                    fontWeight = FontWeight.Bold,
                    fontSize = 20.sp,
                    modifier = Modifier.padding(16.dp),
                    color = MaterialTheme.colorScheme.primary
                )
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    items(tasksList) { task ->
                        StudyTaskCard(task)
                    }
                }
            }
        }
    }
}

@Composable
fun StudyTaskCard(task: StudyTask) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Row(
            modifier = Modifier.padding(16.dp).fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier.size(50.dp).clip(CircleShape).background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Default.Star, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
            }
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(task.title, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                Text("Suggested time: ${task.duration}", color = MaterialTheme.colorScheme.secondary, fontSize = 14.sp)
                Spacer(modifier = Modifier.height(4.dp))
                Text("Why? ${task.reason}", color = Color.Gray, fontSize = 12.sp, fontStyle = androidx.compose.ui.text.font.FontStyle.Italic)
            }
            Checkbox(checked = false, onCheckedChange = {})
        }
    }
}
