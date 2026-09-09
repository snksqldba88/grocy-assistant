package com.example.grocyassistant

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import androidx.compose.runtime.rememberCoroutineScope
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            GrocyAssistantScreen()
        }
    }
}

@androidx.compose.runtime.Composable

fun GrocyAssistantScreen() {

    var message by remember {
        mutableStateOf("")
    }

    var messages by remember {
        mutableStateOf(
            listOf(
                "assistant" to "Hello! I'm Grocy Assistant."
            )
        )
    }

    var sending by remember {
        mutableStateOf(false)
    }

    val scope = rememberCoroutineScope()

    val listState = androidx.compose.foundation.lazy.rememberLazyListState()

    androidx.compose.runtime.LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.lastIndex)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {

        Text(
            text = "Grocy Assistant"
        )

        androidx.compose.foundation.lazy.LazyColumn(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(top = 16.dp),
            state = listState,
            verticalArrangement = androidx.compose.foundation.layout.Arrangement.spacedBy(8.dp)
        ) {

            items(messages.size) { index ->

                val (sender, text) = messages[index]

                Text(
                    text = if (sender == "user") {
                        "You: $text"
                    } else {
                        "Assistant: $text"
                    },
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 8.dp)
        ) {

            OutlinedTextField(
                value = message,
                onValueChange = {
                    message = it
                },
                modifier = Modifier.weight(1f),
                placeholder = {
                    Text("Type a message...")
                },
                enabled = !sending
            )

            Button(
                onClick = {

                    val text = message.trim()

                    if (text.isNotEmpty() && !sending) {

                        message = ""

                        messages = messages +
                                ("user" to text)

                        sending = true

                        scope.launch {

                            try {

                                val result = sendMessage(text)

                                messages = messages +
                                        ("assistant" to result)

                            } catch (e: Exception) {

                                messages = messages +
                                        ("assistant" to "❌ Error: ${e.message}")

                            } finally {

                                sending = false
                            }
                        }
                    }
                },
                modifier = Modifier.padding(start = 8.dp),
                enabled = !sending
            ) {
                Text("Send")
            }
        }
    }
}

suspend fun sendMessage(message: String): String {

    return withContext(Dispatchers.IO) {

        val client = OkHttpClient()

        val json = JSONObject()
        json.put("message", message)

        val body = json.toString()
            .toRequestBody(
                "application/json".toMediaType()
            )

        val request = Request.Builder()
            .url("https://grocy-asst.tail4ee59e.ts.net/api/chat")
            .post(body)
            .build()

        client.newCall(request).execute().use { response ->

            if (!response.isSuccessful) {
                throw Exception(
                    "HTTP ${response.code}"
                )
            }

            val responseBody = response.body?.string()
                ?: throw Exception("Empty response")

            val result = JSONObject(responseBody)

            result.getString("response")
        }
    }
}