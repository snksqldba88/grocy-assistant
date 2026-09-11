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
}

class SettingsDataStore(
    private val context: Context
) {

    val assistantApiUrl: Flow<String?> =
        context.dataStore.data.map { preferences ->
            preferences[SettingsKeys.assistantApiUrl]
        }

    suspend fun saveAssistantApiUrl(
        url: String
    ) {
        context.dataStore.edit { preferences ->
            preferences[SettingsKeys.assistantApiUrl] = url
        }
    }

    suspend fun clearAssistantApiUrl() {
        context.dataStore.edit { preferences ->
            preferences.remove(SettingsKeys.assistantApiUrl)
        }
    }
}