package com.auraface.auraface_app.presentation.placement

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Work
import androidx.compose.material.icons.filled.Event
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Code
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.auraface.auraface_app.data.remote.dto.StudentReadinessDto

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PlacementReadinessScreen(
    navController: androidx.navigation.NavController,
    viewModel: PlacementViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    // Dialog States
    var showSkillDialog by remember { mutableStateOf(false) }
    var showProjectDialog by remember { mutableStateOf(false) }
    var showCertDialog by remember { mutableStateOf(false) }
    var showInternDialog by remember { mutableStateOf(false) }
    var showEventDialog by remember { mutableStateOf(false) }

    Scaffold(
        topBar = { 
            TopAppBar(
                title = { Text("Placement Readiness") },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(imageVector = Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            ) 
        }
    ) { padding ->
        Box(modifier = Modifier.padding(padding)) {
            when (val s = state) {
                is PlacementState.Loading -> CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
                is PlacementState.Error -> Text("Error: ${s.message}", color = Color.Red, modifier = Modifier.align(Alignment.Center))
                is PlacementState.Success -> {
                    ReadinessContent(
                        data = s.data,
                        onAddSkill = { showSkillDialog = true },
                        onAddProject = { showProjectDialog = true },
                        onAddCert = { showCertDialog = true },
                        onAddIntern = { showInternDialog = true },
                        onAddEvent = { showEventDialog = true }
                    )
                }
            }
        }
        
        if (showSkillDialog) {
            AddSkillDialog(onDismiss = { showSkillDialog = false }) { name, level, file ->
                viewModel.addSkill(name, level, file)
                showSkillDialog = false
            }
        }
        
        if (showProjectDialog) {
            AddProjectDialog(onDismiss = { showProjectDialog = false }) { title, desc, stack, file ->
                viewModel.addProject(title, desc, stack, file)
                showProjectDialog = false
            }
        }

        if (showCertDialog) {
            AddCertDialog(onDismiss = { showCertDialog = false }) { name, issuer, file ->
                viewModel.addCertification(name, issuer, file)
                showCertDialog = false
            }
        }
        
        if (showInternDialog) {
             AddInternDialog(onDismiss = { showInternDialog = false }) { company, role, date, file ->
                 viewModel.addInternship(company, role, date, file)
                 showInternDialog = false
             }
        }
        
        if (showEventDialog) {
            AddEventDialog(onDismiss = { showEventDialog = false }) { name, type, date, file ->
                viewModel.addEvent(name, type, date, file)
                showEventDialog = false
            }
        }
    }
}

@Composable
fun ReadinessContent(
    data: StudentReadinessDto,
    onAddSkill: () -> Unit,
    onAddProject: () -> Unit,
    onAddCert: () -> Unit,
    onAddIntern: () -> Unit,
    onAddEvent: () -> Unit
) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Summary Card
        item {
            Card(
                shape = RoundedCornerShape(24.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 8.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(
                            brush = androidx.compose.ui.graphics.Brush.linearGradient(
                                colors = listOf(Color(0xFF6A11CB), Color(0xFF2575FC))
                            )
                        )
                ) {
                    Column(modifier = Modifier.padding(24.dp)) {
                        Text(
                            text = "Overall Readiness",
                            style = MaterialTheme.typography.titleMedium,
                            color = Color.White.copy(alpha = 0.85f)
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Row(verticalAlignment = Alignment.Bottom) {
                            Text(
                                text = "${data.total_score}",
                                style = MaterialTheme.typography.displayMedium,
                                fontWeight = FontWeight.ExtraBold,
                                color = Color.White
                            )
                            Text(
                                text = "%",
                                style = MaterialTheme.typography.headlineSmall,
                                color = Color.White.copy(alpha = 0.85f),
                                modifier = Modifier.padding(bottom = 6.dp, start = 4.dp)
                            )
                        }

                        Spacer(modifier = Modifier.height(16.dp))
                        
                        LinearProgressIndicator(
                            progress = { data.total_score / 100f },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(8.dp)
                                .clip(RoundedCornerShape(4.dp)),
                            color = Color(0xFF00E676), // vibrant green
                            trackColor = Color.White.copy(alpha = 0.2f)
                        )
                        
                        if (data.missing_elements.isNotEmpty()) {
                            Spacer(modifier = Modifier.height(20.dp))
                            Surface(
                                shape = RoundedCornerShape(16.dp),
                                color = Color.White.copy(alpha = 0.15f),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Column(modifier = Modifier.padding(16.dp)) {
                                    Text(
                                        "Areas to Improve:", 
                                        style = MaterialTheme.typography.labelLarge, 
                                        color = Color.White,
                                        fontWeight = FontWeight.Bold
                                    )
                                    Spacer(modifier = Modifier.height(8.dp))
                                    data.missing_elements.take(3).forEach {
                                        Row(
                                            verticalAlignment = Alignment.CenterVertically,
                                            modifier = Modifier.padding(vertical = 4.dp)
                                        ) {
                                            Icon(
                                                imageVector = Icons.Default.Info,
                                                contentDescription = null,
                                                tint = Color(0xFFFFD54F),
                                                modifier = Modifier.size(16.dp)
                                            )
                                            Spacer(modifier = Modifier.width(8.dp))
                                            Text(
                                                it, 
                                                style = MaterialTheme.typography.bodyMedium, 
                                                color = Color.White.copy(alpha = 0.95f)
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // Skills Section
        item { SectionHeader("Technical Skills", onAddSkill, Icons.Default.Code) }
        if (data.skills.isEmpty()) item { EmptyState("No skills added yet.", Icons.Default.Build) }
        items(data.skills) { skill ->
            PremiumListItem(
                title = skill.skill_name,
                subtitle = "Proficiency: ${skill.proficiency}",
                iconText = skill.skill_name.take(1).uppercase(),
                gradient = listOf(Color(0xFFFDC830), Color(0xFFF37335))
            )
        }
        
        // Projects Section
        item { SectionHeader("Projects", onAddProject, Icons.Default.Star) }
        if (data.projects.isEmpty()) item { EmptyState("No projects added yet.", Icons.Default.Star) }
        items(data.projects) { proj ->
            PremiumListItem(
                title = proj.title,
                subtitle = proj.tech_stack,
                iconText = proj.title.take(1).uppercase(),
                gradient = listOf(Color(0xFF00B4DB), Color(0xFF0083B0)),
                trailingText = proj.approval_status
            )
        }

        // Certifications Section
        item { SectionHeader("Certifications", onAddCert, Icons.Default.Star) }
        if (data.certifications.isEmpty()) item { EmptyState("No certifications added yet.", Icons.Default.Star) }
        items(data.certifications) { cert ->
             PremiumListItem(
                title = cert.name,
                subtitle = cert.issuing_org,
                iconText = cert.name.take(1).uppercase(),
                gradient = listOf(Color(0xFF43CEA2), Color(0xFF185A9D)),
                trailingText = cert.verification_status
            )
        }
        
        // Internships Section
        item { SectionHeader("Internships", onAddIntern, Icons.Default.Work) }
        if (data.internships.isEmpty()) item { EmptyState("No internships added yet.", Icons.Default.Work) }
        items(data.internships) { intern ->
             PremiumListItem(
                title = intern.role,
                subtitle = intern.company_name,
                iconText = intern.company_name.take(1).uppercase(),
                gradient = listOf(Color(0xFF8E2DE2), Color(0xFF4A00E0)),
                trailingText = intern.verification_status
            )
        }

        // Events Section
        item { SectionHeader("Events & Hackathons", onAddEvent, Icons.Default.Event) }
        if (data.events.isEmpty()) item { EmptyState("No events added yet.", Icons.Default.Event) }
        items(data.events) { event ->
             PremiumListItem(
                title = event.event_name,
                subtitle = event.event_type,
                iconText = event.event_name.take(1).uppercase(),
                gradient = listOf(Color(0xFFFF416C), Color(0xFFFF4B2B))
            )
        }
        
        item { Spacer(modifier = Modifier.height(32.dp)) }
    }
}

@Composable
fun PremiumListItem(
    title: String,
    subtitle: String,
    iconText: String,
    gradient: List<Color>,
    trailingText: String? = null
) {
    Card(
        shape = RoundedCornerShape(16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(brush = androidx.compose.ui.graphics.Brush.linearGradient(colors = gradient)),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = iconText,
                    style = MaterialTheme.typography.titleLarge,
                    color = Color.White,
                    fontWeight = FontWeight.Bold
                )
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            if (trailingText != null) {
                val isPending = trailingText.contains("Pending", ignoreCase = true)
                val isApproved = trailingText.contains("Approved", ignoreCase = true) || trailingText.contains("Verified", ignoreCase = true)
                
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = if (isPending) Color(0xFFFFF3E0) 
                            else if (isApproved) Color(0xFFE8F5E9)
                            else MaterialTheme.colorScheme.secondaryContainer
                ) {
                    Text(
                        text = trailingText,
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        color = if (isPending) Color(0xFFEF6C00) 
                                else if (isApproved) Color(0xFF2E7D32)
                                else MaterialTheme.colorScheme.onSecondaryContainer
                    )
                }
            }
        }
    }
}

@Composable
fun SectionHeader(title: String, onAdd: () -> Unit, icon: androidx.compose.ui.graphics.vector.ImageVector) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 16.dp, bottom = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                title, 
                style = MaterialTheme.typography.titleMedium, 
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
        }
        IconButton(
            onClick = onAdd,
            modifier = Modifier
                .size(36.dp)
                .background(MaterialTheme.colorScheme.primaryContainer, CircleShape)
        ) {
            Icon(Icons.Default.Add, contentDescription = "Add $title", tint = MaterialTheme.colorScheme.onPrimaryContainer, modifier = Modifier.size(20.dp))
        }
    }
}

@Composable
fun EmptyState(text: String, icon: androidx.compose.ui.graphics.vector.ImageVector) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = Color.Gray.copy(alpha = 0.4f),
            modifier = Modifier.size(48.dp)
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = text, 
            style = MaterialTheme.typography.bodyMedium, 
            color = Color.Gray
        )
    }
}

// --- Dialogs ---

@Composable
fun AddSkillDialog(onDismiss: () -> Unit, onConfirm: (String, String, java.io.File?) -> Unit) {
    var name by remember { mutableStateOf("") }
    var level by remember { mutableStateOf("Beginner") }
    var selectedFile by remember { mutableStateOf<android.net.Uri?>(null) }
    
    val context = androidx.compose.ui.platform.LocalContext.current
    val contentResolver = context.contentResolver
    
    val launcher = androidx.activity.compose.rememberLauncherForActivityResult(
        contract = androidx.activity.result.contract.ActivityResultContracts.GetContent()
    ) { uri: android.net.Uri? ->
        selectedFile = uri
    }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Add Skill") },
        text = {
            Column {
                OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("Skill Name") })
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(value = level, onValueChange = { level = it }, label = { Text("Proficiency") })
                Spacer(modifier = Modifier.height(8.dp))
                Button(onClick = { launcher.launch("*/*") }) {
                    Text(if (selectedFile != null) "File Selected" else "Attach Proof (Optional)")
                }
                if (selectedFile != null) {
                    Text(selectedFile!!.lastPathSegment ?: "File", style = MaterialTheme.typography.bodySmall)
                }
            }
        },
        confirmButton = {
            TextButton(onClick = { 
                if(name.isNotBlank()) {
                    var file: java.io.File? = null
                    if (selectedFile != null) {
                        try {
                            val inputStream = contentResolver.openInputStream(selectedFile!!)
                            val tempFile = java.io.File.createTempFile("skill_", ".tmp", context.cacheDir)
                            tempFile.outputStream().use { output ->
                                inputStream?.copyTo(output)
                            }
                            file = tempFile
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }
                    onConfirm(name, level, file)
                }
            }) { Text("Add") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancel") }
        }
    )
}

@Composable
fun AddProjectDialog(onDismiss: () -> Unit, onConfirm: (String, String, String, java.io.File?) -> Unit) {
    var title by remember { mutableStateOf("") }
    var desc by remember { mutableStateOf("") }
    var stack by remember { mutableStateOf("") }
    var selectedFile by remember { mutableStateOf<android.net.Uri?>(null) }
    
    val context = androidx.compose.ui.platform.LocalContext.current
    val contentResolver = context.contentResolver
    
    val launcher = androidx.activity.compose.rememberLauncherForActivityResult(
        contract = androidx.activity.result.contract.ActivityResultContracts.GetContent()
    ) { uri: android.net.Uri? ->
        selectedFile = uri
    }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Add Project") },
        text = {
            Column {
                OutlinedTextField(value = title, onValueChange = { title = it }, label = { Text("Project Title") })
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(value = desc, onValueChange = { desc = it }, label = { Text("Description") })
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(value = stack, onValueChange = { stack = it }, label = { Text("Tech Stack (e.g. Kotlin, Python)") })
                Spacer(modifier = Modifier.height(8.dp))
                Button(onClick = { launcher.launch("*/*") }) {
                    Text(if (selectedFile != null) "File Selected" else "Attach Proof (Optional)")
                }
                if (selectedFile != null) {
                    Text(selectedFile!!.lastPathSegment ?: "File", style = MaterialTheme.typography.bodySmall)
                }
            }
        },
        confirmButton = {
            TextButton(onClick = { 
                if(title.isNotBlank()) {
                    var file: java.io.File? = null
                    if (selectedFile != null) {
                        try {
                            val inputStream = contentResolver.openInputStream(selectedFile!!)
                            val tempFile = java.io.File.createTempFile("proj_", ".tmp", context.cacheDir)
                            tempFile.outputStream().use { output ->
                                inputStream?.copyTo(output)
                            }
                            file = tempFile
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }
                    onConfirm(title, desc, stack, file)
                }
            }) { Text("Add") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancel") }
        }
    )
}

@Composable
fun AddCertDialog(onDismiss: () -> Unit, onConfirm: (String, String, java.io.File?) -> Unit) {
    var name by remember { mutableStateOf("") }
    var issuer by remember { mutableStateOf("") }
    var selectedFile by remember { mutableStateOf<android.net.Uri?>(null) }
    
    val context = androidx.compose.ui.platform.LocalContext.current
    val contentResolver = context.contentResolver
    
    val launcher = androidx.activity.compose.rememberLauncherForActivityResult(
        contract = androidx.activity.result.contract.ActivityResultContracts.GetContent()
    ) { uri: android.net.Uri? ->
        selectedFile = uri
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Add Certification") },
        text = {
            Column {
                OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("Certificate Name") })
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(value = issuer, onValueChange = { issuer = it }, label = { Text("Issuing Organization") })
                Spacer(modifier = Modifier.height(8.dp))
                
                Button(onClick = { launcher.launch("*/*") }) {
                    Text(if (selectedFile != null) "File Selected" else "Attach Certificate (PDF/Image)")
                }
                if (selectedFile != null) {
                    Text(selectedFile!!.lastPathSegment ?: "File", style = MaterialTheme.typography.bodySmall)
                }
            }
        },
        confirmButton = {
            TextButton(onClick = { 
                if(name.isNotBlank()) {
                    var file: java.io.File? = null
                    if (selectedFile != null) {
                        // Create a temporary file from the URI
                        try {
                            val inputStream = contentResolver.openInputStream(selectedFile!!)
                             val tempFile = java.io.File.createTempFile("cert_", ".tmp", context.cacheDir)
                             tempFile.outputStream().use { output ->
                                 inputStream?.copyTo(output)
                             }
                             file = tempFile
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }
                    onConfirm(name, issuer, file)
                }
            }) { Text("Add") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancel") }
        }
    )
}

@Composable
fun AddInternDialog(onDismiss: () -> Unit, onConfirm: (String, String, String, java.io.File?) -> Unit) {
    var company by remember { mutableStateOf("") }
    var role by remember { mutableStateOf("") }
    var date by remember { mutableStateOf("2024-01-01") } // Placeholder, need DatePicker ideally
    var selectedFile by remember { mutableStateOf<android.net.Uri?>(null) }
    
    val context = androidx.compose.ui.platform.LocalContext.current
    val contentResolver = context.contentResolver
    
    val launcher = androidx.activity.compose.rememberLauncherForActivityResult(
        contract = androidx.activity.result.contract.ActivityResultContracts.GetContent()
    ) { uri: android.net.Uri? ->
        selectedFile = uri
    }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Add Internship") },
        text = {
            Column {
                OutlinedTextField(value = company, onValueChange = { company = it }, label = { Text("Company Name") })
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(value = role, onValueChange = { role = it }, label = { Text("Role") })
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(value = date, onValueChange = { date = it }, label = { Text("Start Date (YYYY-MM-DD)") }, placeholder = { Text("2024-01-01") })
                Spacer(modifier = Modifier.height(8.dp))
                Button(onClick = { launcher.launch("*/*") }) {
                    Text(if (selectedFile != null) "File Selected" else "Attach Proof (Optional)")
                }
                if (selectedFile != null) {
                    Text(selectedFile!!.lastPathSegment ?: "File", style = MaterialTheme.typography.bodySmall)
                }
            }
        },
        confirmButton = {
            TextButton(onClick = { 
                if(company.isNotBlank()) {
                    var file: java.io.File? = null
                    if (selectedFile != null) {
                        try {
                            val inputStream = contentResolver.openInputStream(selectedFile!!)
                            val tempFile = java.io.File.createTempFile("intern_", ".tmp", context.cacheDir)
                            tempFile.outputStream().use { output ->
                                inputStream?.copyTo(output)
                            }
                            file = tempFile
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }
                    onConfirm(company, role, date, file)
                }
            }) { Text("Add") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancel") }
        }
    )
}

@Composable
fun AddEventDialog(onDismiss: () -> Unit, onConfirm: (String, String, String, java.io.File?) -> Unit) {
    var name by remember { mutableStateOf("") }
    var type by remember { mutableStateOf("Hackathon") }
    var date by remember { mutableStateOf("2024-01-01") } 
    var selectedFile by remember { mutableStateOf<android.net.Uri?>(null) }
    
    val context = androidx.compose.ui.platform.LocalContext.current
    val contentResolver = context.contentResolver
    
    val launcher = androidx.activity.compose.rememberLauncherForActivityResult(
        contract = androidx.activity.result.contract.ActivityResultContracts.GetContent()
    ) { uri: android.net.Uri? ->
        selectedFile = uri
    }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Add Event") },
        text = {
            Column {
                OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("Event Name") })
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(value = type, onValueChange = { type = it }, label = { Text("Type (e.g. Hackathon, Workshop)") })
                 Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(value = date, onValueChange = { date = it }, label = { Text("Date (YYYY-MM-DD)") })
                Spacer(modifier = Modifier.height(8.dp))
                Button(onClick = { launcher.launch("*/*") }) {
                    Text(if (selectedFile != null) "File Selected" else "Attach Proof (Optional)")
                }
                if (selectedFile != null) {
                    Text(selectedFile!!.lastPathSegment ?: "File", style = MaterialTheme.typography.bodySmall)
                }
            }
        },
        confirmButton = {
            TextButton(onClick = { 
                if(name.isNotBlank()) {
                    var file: java.io.File? = null
                    if (selectedFile != null) {
                        try {
                            val inputStream = contentResolver.openInputStream(selectedFile!!)
                            val tempFile = java.io.File.createTempFile("event_", ".tmp", context.cacheDir)
                            tempFile.outputStream().use { output ->
                                inputStream?.copyTo(output)
                            }
                            file = tempFile
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }
                    onConfirm(name, type, date, file)
                }
            }) { Text("Add") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancel") }
        }
    )
}
