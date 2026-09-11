package com.example.grocyassistant

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.grocyassistant.data.AssistantRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import com.example.grocyassistant.assistant.StockQuery
import com.example.grocyassistant.assistant.StockGroupQuery

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

                val lowerText =
                    text.lowercase()

                if (lowerText.startsWith("stock ")) {

                    val groupName =
                        text.substringAfter("stock ")
                            .trim()

                    val groupQuery =
                        StockGroupQuery(
                            getApplication<Application>()
                        )

                    val stock =
                        groupQuery.findStockByGroup(
                            groupName
                        )

                    if (stock.isNotEmpty()) {

                        val result =
                            buildString {

                                appendLine(
                                    "Stock in $groupName:"
                                )

                                appendLine()

                                stock.forEach {
                                    appendLine(
                                        "${it.productName}: ${it.amount}"
                                    )
                                }
                            }.trim()

                        _messages.value =
                            _messages.value +
                                    ("assistant" to result)

                        return@launch
                    }
                }

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

    fun testStockQuery() {

        viewModelScope.launch {

            try {

                val query =
                    StockQuery(
                        getApplication<Application>()
                    )

                val stock =
                    query.findStock("tomato")

                val result =
                    if (stock != null) {

                        """
                    Product: ${stock.productName}
                    Product ID: ${stock.productId}
                    Amount: ${stock.amount}
                    Unit ID: ${stock.unitId ?: "Unknown"}
                    Location ID: ${stock.locationId ?: "Unknown"}
                    """.trimIndent()

                    } else {

                        "Tomato stock was not found."
                    }

                _messages.value =
                    _messages.value +
                            ("assistant" to result)

            } catch (e: Exception) {

                _messages.value =
                    _messages.value +
                            (
                                    "assistant" to
                                            "❌ Stock query test error: ${e.message}"
                                    )
            }
        }
    }

    fun testStockGroupQuery() {
        viewModelScope.launch {
            try {
                val query =
                    StockGroupQuery(
                        getApplication<Application>()
                    )

                val stock =
                    query.findStockByGroup("vegetables")

                val result =
                    if (stock.isNotEmpty()) {
                        buildString {
                            appendLine("Vegetables stock:")
                            appendLine()

                            stock.forEach {
                                appendLine(
                                    "${it.productName}: ${it.amount}"
                                )
                            }
                        }.trim()
                    } else {
                        "No vegetables found in stock."
                    }

                _messages.value =
                    _messages.value +
                            ("assistant" to result)

            } catch (e: Exception) {
                _messages.value =
                    _messages.value +
                            (
                                    "assistant" to
                                            "❌ Stock group query test error: ${e.message}"
                                    )
            }
        }
    }
}