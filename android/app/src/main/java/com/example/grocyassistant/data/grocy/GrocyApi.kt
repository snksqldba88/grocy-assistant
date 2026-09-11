package com.example.grocyassistant.data.grocy

import android.content.Context
import com.example.grocyassistant.settings.SettingsDataStore
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject

class GrocyApi(
    private val context: Context
) {

    private val httpClient = OkHttpClient()

    suspend fun get(
        path: String
    ): JSONObject {
        return withContext(Dispatchers.IO) {

            val settingsDataStore =
                SettingsDataStore(context)

            val baseUrl =
                settingsDataStore.grocyUrl.first()
                    ?.trim()
                    ?.trimEnd('/')
                    ?: throw Exception(
                        "Grocy URL is not configured"
                    )

            val apiKey =
                settingsDataStore.grocyApiKey.first()
                    ?.trim()
                    ?.takeIf { it.isNotEmpty() }
                    ?: throw Exception(
                        "Grocy API key is not configured"
                    )

            val request =
                Request.Builder()
                    .url("$baseUrl$path")
                    .header(
                        "GROCY-API-KEY",
                        apiKey
                    )
                    .get()
                    .build()

            httpClient.newCall(request)
                .execute()
                .use { response ->

                    if (!response.isSuccessful) {
                        throw Exception(
                            "Grocy HTTP ${response.code}"
                        )
                    }

                    val responseBody =
                        response.body?.string()
                            ?: throw Exception(
                                "Empty Grocy response"
                            )

                    JSONObject(responseBody)
                }
        }
    }

    suspend fun getSystemInfo(): JSONObject {
        return get("/api/system/info")
    }
}