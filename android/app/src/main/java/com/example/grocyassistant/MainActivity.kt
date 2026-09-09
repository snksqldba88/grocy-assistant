package com.example.grocyassistant

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowUpward
import androidx.compose.foundation.background
import androidx.compose.ui.Alignment
import androidx.compose.material3.Surface
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.graphics.Color
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

    val listState =
        androidx.compose.foundation.lazy.rememberLazyListState()

    androidx.compose.runtime.LaunchedEffect(messages.size, sending) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(
                if (sending) messages.size else messages.lastIndex
            )
        }
    }

    Surface(
        modifier = Modifier.fillMaxSize(),
        shape = RoundedCornerShape(24.dp),
        color = Color.White
    ) {

        Column(
            modifier = Modifier.fillMaxSize()
        ) {

            Text(
                text = "Grocy Assistant",
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        color = Color(0xFF1976D2)
                    )
                    .padding(
                        horizontal = 16.dp,
                        vertical = 14.dp
                    ),
                color = Color.White,
                style = androidx.compose.material3.MaterialTheme.typography.headlineSmall
            )

            androidx.compose.foundation.lazy.LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .padding(
                        top = 8.dp,
                        bottom = 8.dp
                    ),
                state = listState,
                verticalArrangement =
                    Arrangement.spacedBy(8.dp)
            ) {

                items(messages.size) { index ->

                    val (sender, text) = messages[index]

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = if (sender == "user") {
                            Arrangement.End
                        } else {
                            Arrangement.Start
                        }
                    ) {

                        Text(
                            text = text,
                            modifier = Modifier
                                .background(
                                    color = if (sender == "user") {
                                        Color(0xFFE3F2FD)
                                    } else {
                                        Color(0xFFF1F1F1)
                                    },
                                    shape = RoundedCornerShape(16.dp)
                                )
                                .padding(
                                    horizontal = 16.dp,
                                    vertical = 10.dp
                                )
                        )
                    }
                }

                if (sending) {

                    item {

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.Start
                        ) {

                            Text(
                                text = "Sending…",
                                modifier = Modifier
                                    .background(
                                        color = Color(0xFFF1F1F1),
                                        shape = RoundedCornerShape(16.dp)
                                    )
                                    .padding(
                                        horizontal = 16.dp,
                                        vertical = 10.dp
                                    )
                            )
                        }
                    }
                }
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(
                        top = 8.dp,
                        bottom = 12.dp
                    ),
                verticalAlignment = Alignment.CenterVertically
            ) {

                OutlinedTextField(
                    value = message,
                    onValueChange = {
                        message = it
                    },
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = {
                        Text("Message Grocy Assistant")
                    },
                    enabled = !sending,
                    singleLine = true,
                    shape = RoundedCornerShape(28.dp),
                    trailingIcon = {

                        IconButton(
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
                                                    (
                                                            "assistant" to
                                                                    "❌ Error: ${e.message}"
                                                            )

                                        } finally {

                                            sending = false
                                        }
                                    }
                                }
                            },
                            enabled = message.trim().isNotEmpty() && !sending,
                            modifier = Modifier
                                .size(40.dp)
                                .padding(end = 4.dp)
                        ) {

                            Icon(
                                imageVector = Icons.Default.ArrowUpward,
                                contentDescription = "Send"
                            )
                        }
                    },
                    keyboardOptions = androidx.compose.foundation.text.KeyboardOptions(
                        imeAction = androidx.compose.ui.text.input.ImeAction.Send
                    ),
                    keyboardActions = androidx.compose.foundation.text.KeyboardActions(
                        onSend = {

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
                                                (
                                                        "assistant" to
                                                                "❌ Error: ${e.message}"
                                                        )

                                    } finally {

                                        sending = false
                                    }
                                }
                            }
                        }
                    )
                )
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