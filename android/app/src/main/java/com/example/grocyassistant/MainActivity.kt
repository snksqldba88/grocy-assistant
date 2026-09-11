package com.example.grocyassistant

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowUpward
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.time.Duration.Companion.milliseconds
import com.example.grocyassistant.data.sendMessage
import androidx.compose.material.icons.filled.Settings
import androidx.compose.runtime.mutableIntStateOf
//import androidx.compose.runtime.getValue
//import androidx.compose.runtime.mutableStateOf
//import androidx.compose.runtime.remember
//import androidx.compose.runtime.setValue
import com.example.grocyassistant.settings.SettingsDataStore
import com.example.grocyassistant.settings.SettingsScreen

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            var showSettings by remember {
                mutableStateOf(false)
            }

            val settingsDataStore =
                remember {
                    SettingsDataStore(applicationContext)
                }

            if (showSettings) {
                SettingsScreen(
                    settingsDataStore = settingsDataStore,
                    onBack = {
                        showSettings = false
                    }
                )
            } else {
                GrocyAssistantScreen(
                    onSettingsClick = {
                        showSettings = true
                    }
                )
            }
        }
    }
}

@Composable
fun GrocyAssistantScreen(
    onSettingsClick: () -> Unit
) {

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

    val listState = rememberLazyListState()

    /*
     * Automatically scroll to the newest message.
     */
    LaunchedEffect(messages.size, sending) {

        val itemCount =
            messages.size + if (sending) 1 else 0

        if (itemCount > 0) {

            listState.animateScrollToItem(
                itemCount - 1
            )
        }
    }

    /*
     * Sends the current message.
     *
     * Both the send button and keyboard Send action
     * use this same function.
     */
    fun sendCurrentMessage() {

        val text = message.trim()

        if (text.isEmpty() || sending) {
            return
        }

        message = ""

        messages =
            messages + ("user" to text)

        sending = true

        scope.launch {

            try {

                val result =
                    sendMessage(text)

                messages =
                    messages +
                            ("assistant" to result)

            } catch (e: Exception) {

                messages =
                    messages +
                            (
                                    "assistant" to
                                            "❌ Error: ${e.message}"
                                    )

            } finally {

                sending = false
            }
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

            /*
             * Blue header.
             *
             * Kept exactly as before.
             */
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        color = Color(0xFF1976D2)
                    )
                    .padding(
                        horizontal = 16.dp,
                        vertical = 8.dp
                    ),
                verticalAlignment = Alignment.CenterVertically
            ) {

                Text(
                    text = "Grocy Assistant",
                    modifier = Modifier.weight(1f),
                    color = Color.White,
                    style = MaterialTheme.typography.headlineSmall
                )

                IconButton(
                    onClick = onSettingsClick
                ) {
                    Icon(
                        imageVector = Icons.Default.Settings,
                        contentDescription = "Settings",
                        tint = Color.White
                    )
                }
            }

            /*
             * Conversation
             */
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .padding(
                        top = 12.dp,
                        bottom = 8.dp
                    ),
                state = listState,
                verticalArrangement =
                    Arrangement.spacedBy(6.dp)
            ) {

                items(messages.size) { index ->

                    val (sender, text) =
                        messages[index]

                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(
                                horizontal = 12.dp,
                                vertical = 2.dp
                            ),
                        horizontalArrangement =
                            if (sender == "user") {
                                Arrangement.End
                            } else {
                                Arrangement.Start
                            }
                    ) {

                        Text(
                            text = text,
                            modifier = Modifier
                                .widthIn(
                                    max = 300.dp
                                )
                                .background(
                                    color =
                                        if (sender == "user") {
                                            Color(0xFF1976D2)
                                        } else {
                                            Color(0xFFF1F1F1)
                                        },
                                    shape =
                                        RoundedCornerShape(
                                            topStart = 18.dp,
                                            topEnd = 18.dp,
                                            bottomStart =
                                                if (sender == "user") {
                                                    18.dp
                                                } else {
                                                    4.dp
                                                },
                                            bottomEnd =
                                                if (sender == "user") {
                                                    4.dp
                                                } else {
                                                    18.dp
                                                }
                                        )
                                )
                                .padding(
                                    horizontal = 14.dp,
                                    vertical = 10.dp
                                ),
                            color =
                                if (sender == "user") {
                                    Color.White
                                } else {
                                    Color(0xFF202124)
                                },
                            style =
                                MaterialTheme.typography.bodyLarge
                        )
                    }
                }

                /*
                 * Animated typing indicator.
                 */
                if (sending) {

                    item {

                        TypingIndicator()
                    }
                }
            }

            /*
             * Message composer
             */
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(
                        horizontal = 12.dp,
                        vertical = 10.dp
                    ),
                verticalAlignment =
                    Alignment.CenterVertically
            ) {

                OutlinedTextField(
                    value = message,
                    onValueChange = {
                        message = it
                    },
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = {
                        Text(
                            "Message Grocy Assistant"
                        )
                    },
                    enabled = !sending,
                    singleLine = true,
                    shape =
                        RoundedCornerShape(28.dp),

                    trailingIcon = {

                        IconButton(
                            onClick = {
                                sendCurrentMessage()
                            },
                            enabled =
                                message.trim().isNotEmpty() &&
                                        !sending
                        ) {

                            Icon(
                                imageVector =
                                    Icons.Default.ArrowUpward,
                                contentDescription =
                                    "Send"
                            )
                        }
                    },

                    keyboardOptions =
                        KeyboardOptions(
                            imeAction =
                                ImeAction.Send
                        ),

                    keyboardActions =
                        KeyboardActions(
                            onSend = {
                                sendCurrentMessage()
                            }
                        )
                )
            }
        }
    }
}

/*
 * Simple animated typing indicator.
 *
 * No additional libraries are required.
 */
@Composable
fun TypingIndicator() {

    var dots by remember {
        mutableIntStateOf(1)
    }

    LaunchedEffect(Unit) {

        while (true) {

            delay(400.milliseconds)

            dots = when (dots) {
                1 -> 2
                2 -> 3
                else -> 1
            }
        }
    }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(
                horizontal = 12.dp,
                vertical = 2.dp
            ),
        horizontalArrangement =
            Arrangement.Start
    ) {

        Text(
            text = "•".repeat(dots),
            modifier = Modifier
                .background(
                    color = Color(0xFFF1F1F1),
                    shape = RoundedCornerShape(
                        topStart = 18.dp,
                        topEnd = 18.dp,
                        bottomStart = 4.dp,
                        bottomEnd = 18.dp
                    )
                )
                .padding(
                    horizontal = 16.dp,
                    vertical = 9.dp
                ),
            color = Color(0xFF666666),
            style =
                MaterialTheme.typography.bodyLarge
        )
    }
}