package com.example.grocyassistant.data

import android.content.Context

class AssistantRepository(
    private val context: Context
) {

    suspend fun sendMessage(
        message: String
    ): String {
        return com.example.grocyassistant.data.sendMessage(
            context,
            message
        )
    }
}