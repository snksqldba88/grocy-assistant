package com.example.grocyassistant

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.grocyassistant.data.AssistantRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class GrocyAssistantViewModel(
    application: Application
) : AndroidViewModel(application) {

    private val repository =
        AssistantRepository(application.applicationContext)

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
                    repository.sendMessage(text)

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

    fun testGrocyConnection(
        onResult: (String) -> Unit
    ) {
        viewModelScope.launch {
            try {
                val grocyApi =
                    com.example.grocyassistant.data.grocy.GrocyApi(
                        getApplication<Application>()
                    )

                val result =
                    grocyApi.getSystemInfo()

                onResult(
                    "Grocy connection successful:\n$result"
                )

            } catch (e: Exception) {
                onResult(
                    "Grocy connection failed:\n${e.message}"
                )
            }
        }
    }
}