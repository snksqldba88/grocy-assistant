package com.example.grocyassistant.settings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch

@Composable
fun SettingsScreen(
    settingsDataStore: SettingsDataStore,
    onBack: () -> Unit
) {
    val scope = rememberCoroutineScope()

    var assistantApiUrl by remember {
        mutableStateOf("")
    }

    var saved by remember {
        mutableStateOf(false)
    }

    LaunchedEffect(Unit) {
        settingsDataStore.assistantApiUrl.collect { url ->
            assistantApiUrl = url ?: ""
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {

        IconButton(
            onClick = onBack
        ) {
            Icon(
                imageVector = Icons.Default.ArrowBack,
                contentDescription = "Back"
            )
        }

        Text(
            text = "Settings",
            style = MaterialTheme.typography.headlineMedium
        )

        OutlinedTextField(
            value = assistantApiUrl,
            onValueChange = {
                assistantApiUrl = it
                saved = false
            },
            modifier = Modifier.fillMaxWidth(),
            label = {
                Text("Assistant API URL")
            },
            singleLine = true
        )

        Button(
            onClick = {
                scope.launch {
                    settingsDataStore.saveAssistantApiUrl(
                        assistantApiUrl.trim()
                    )
                    saved = true
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Save")
        }

        if (saved) {
            Text(
                text = "Settings saved",
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}