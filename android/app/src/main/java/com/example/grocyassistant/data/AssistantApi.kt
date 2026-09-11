package com.example.grocyassistant.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

private const val ASSISTANT_API_URL =
    "https://grocy-asst.tail4ee59e.ts.net/api/chat"

private val httpClient = OkHttpClient()

suspend fun sendMessage(
    message: String
): String {

    return withContext(Dispatchers.IO) {

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
                .url(ASSISTANT_API_URL)
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