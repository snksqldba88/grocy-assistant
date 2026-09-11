package com.example.grocyassistant

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.grocyassistant.data.sendMessage as sendAssistantMessage
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class GrocyAssistantViewModel(
    application: Application
) : AndroidViewModel(application) {

    private val _messages =
        MutableStateFlow(
            listOf(
                "assistant" to "Hello! I'm Grocy Assistant."
            )
        )

    val messages: StateFlow<List<Pair<String, String>>> =
        _messages.asStateFlow()

    private val _sending =
        MutableStateFlow(false)

    val sending: StateFlow<Boolean> =
        _sending.asStateFlow()

    fun sendMessage(message: String) {

        val text = message.trim()

        if (text.isEmpty() || _sending.value) {
            return
        }

        _messages.value =
            _messages.value + ("user" to text)

        _sending.value = true

        viewModelScope.launch {

            try {

                val result =
                    sendAssistantMessage(
                        getApplication<Application>(),
                        text
                    )

                _messages.value =
                    _messages.value +
                            ("assistant" to result)

            } catch (e: Exception) {

                _messages.value =
                    _messages.value +
                            (
                                    "assistant" to
                                            "❌ Error: ${e.message}"
                                    )

            } finally {

                _sending.value = false
            }
        }
    }
}