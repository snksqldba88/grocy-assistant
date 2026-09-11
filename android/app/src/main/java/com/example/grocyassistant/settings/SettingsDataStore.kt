package com.example.grocyassistant.settings

import android.content.Context
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore(
    name = "grocy_assistant_settings"
)

private object SettingsKeys {
    val assistantApiUrl =
        stringPreferencesKey("assistant_api_url")

    val grocyUrl =
        stringPreferencesKey("grocy_url")

    val grocyApiKey =
        stringPreferencesKey("grocy_api_key")
}
class SettingsDataStore(
    private val context: Context
) {

    val assistantApiUrl: Flow<String?> =
        context.dataStore.data.map { preferences ->
            preferences[SettingsKeys.assistantApiUrl]
        }

    val grocyUrl: Flow<String?> =
        context.dataStore.data.map { preferences ->
            preferences[SettingsKeys.grocyUrl]
        }

    val grocyApiKey: Flow<String?> =
        context.dataStore.data.map { preferences ->
            preferences[SettingsKeys.grocyApiKey]
        }

    suspend fun saveAssistantApiUrl(
        url: String
    ) {
        context.dataStore.edit { preferences ->
            preferences[SettingsKeys.assistantApiUrl] = url
        }
    }

    suspend fun saveGrocyUrl(
        url: String
    ) {
        context.dataStore.edit { preferences ->
            preferences[SettingsKeys.grocyUrl] = url
        }
    }

    suspend fun saveGrocyApiKey(
        apiKey: String
    ) {
        context.dataStore.edit { preferences ->
            preferences[SettingsKeys.grocyApiKey] = apiKey
        }
    }

    suspend fun clearAssistantApiUrl() {
        context.dataStore.edit { preferences ->
            preferences.remove(SettingsKeys.assistantApiUrl)
        }
    }

    suspend fun clearGrocyUrl() {
        context.dataStore.edit { preferences ->
            preferences.remove(SettingsKeys.grocyUrl)
        }
    }

    suspend fun clearGrocyApiKey() {
        context.dataStore.edit { preferences ->
            preferences.remove(SettingsKeys.grocyApiKey)
        }
    }
}