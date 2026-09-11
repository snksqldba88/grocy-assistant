package com.example.grocyassistant.data

import android.content.Context
import com.example.grocyassistant.settings.SettingsDataStore
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

private const val DEFAULT_ASSISTANT_API_URL =
    "https://grocy-asst.tail4ee59e.ts.net/api/chat"

private val httpClient = OkHttpClient()

suspend fun sendMessage(
    context: Context,
    message: String
): String {

    return withContext(Dispatchers.IO) {

        val settingsDataStore =
            SettingsDataStore(context)

        val configuredUrl =
            settingsDataStore.assistantApiUrl.first()

        val apiUrl =
            configuredUrl
                ?.trim()
                ?.takeIf { it.isNotEmpty() }
                ?: DEFAULT_ASSISTANT_API_URL

        val json = JSONObject()

        json.put(
            "message",
            message
        )

        val body =
            json.toString()
                .toRequestBody(
                    "application/json".toMediaType()
                )

        val request =
            Request.Builder()
                .url(apiUrl)
                .post(body)
                .build()

        httpClient.newCall(request)
            .execute()
            .use { response ->

                if (!response.isSuccessful) {

                    throw Exception(
                        "HTTP ${response.code}"
                    )
                }

                val responseBody =
                    response.body?.string()
                        ?: throw Exception(
                            "Empty response"
                        )

                val result =
                    JSONObject(responseBody)

                result.getString("response")
            }
    }
}