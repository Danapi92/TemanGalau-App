import React, { useState, useEffect } from 'react';
import { SafeAreaView, View, Text, TextInput, Button, FlatList, TouchableOpacity, Image, StyleSheet } from 'react-native';
import * as Speech from 'expo-speech';
import { Audio } from 'expo-av';

// Edit this to point to your backend during development (e.g. http://10.0.2.2:8000)
const BACKEND_URL = 'http://10.0.2.2:8000';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState('');
  const [recording, setRecording] = useState(null);

  useEffect(() => {}, []);

  const sendText = async () => {
    if (!text.trim()) return;
    const userMsg = { id: Date.now().toString(), role: 'user', text };
    setMessages(prev => [userMsg, ...prev]);
    setText('');

    try {
      const resp = await fetch(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.text })
      });
      const data = await resp.json();
      const botMsg = { id: Date.now().toString() + '-bot', role: 'bot', text: data.reply || '...' };
      setMessages(prev => [botMsg, ...prev]);
      // optional TTS
      Speech.speak(botMsg.text);
    } catch (e) {
      console.error(e);
    }
  };

  const startRecording = async () => {
    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
      const rec = new Audio.Recording();
      await rec.prepareToRecordAsync(Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY);
      await rec.startAsync();
      setRecording(rec);
    } catch (err) {
      console.error('Failed to start recording', err);
    }
  };

  const stopRecording = async () => {
    try {
      if (!recording) return;
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);
      // upload to backend
      const form = new FormData();
      form.append('file', { uri, name: 'speech.wav', type: 'audio/wav' });
      const resp = await fetch(`${BACKEND_URL}/speech`, { method: 'POST', body: form });
      const data = await resp.json();
      const botMsg = { id: Date.now().toString() + '-bot', role: 'bot', text: data.transcript || data.reply || '...' };
      setMessages(prev => [botMsg, ...prev]);
      Speech.speak(botMsg.text);
    } catch (err) {
      console.error('stopRecording error', err);
    }
  };

  const generateImage = async () => {
    try {
      const resp = await fetch(`${BACKEND_URL}/image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: 'a friendly anime companion portrait' })
      });
      const data = await resp.json();
      const imgMsg = { id: Date.now().toString() + '-img', role: 'bot', image: data.url };
      setMessages(prev => [imgMsg, ...prev]);
    } catch (e) {
      console.error(e);
    }
  };

  const renderItem = ({ item }) => (
    <View style={[styles.msgRow, item.role === 'user' ? styles.user : styles.bot]}>
      {item.text ? <Text style={styles.msgText}>{item.text}</Text> : null}
      {item.image ? <Image source={{ uri: item.image }} style={styles.image} /> : null}
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}><Text style={styles.headerText}>TemanGalau (Android)</Text></View>
      <View style={styles.controls}>
        <TextInput style={styles.input} placeholder="Ketik pesan..." value={text} onChangeText={setText} />
        <Button title="Kirim" onPress={sendText} />
        <Button title={recording ? 'Stop' : 'Record'} onPress={recording ? stopRecording : startRecording} />
        <Button title="Generate Image" onPress={generateImage} />
      </View>

      <FlatList data={messages} renderItem={renderItem} keyExtractor={i => i.id} inverted />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  header: { padding: 12, backgroundColor: '#6C63FF' },
  headerText: { color: '#fff', fontWeight: '600', fontSize: 18 },
  controls: { padding: 12, flexDirection: 'row', alignItems: 'center', gap: 8 },
  input: { flex: 1, borderWidth: 1, borderColor: '#ddd', padding: 8, marginRight: 8, borderRadius: 6 },
  msgRow: { margin: 8, padding: 12, borderRadius: 10, maxWidth: '80%' },
  user: { alignSelf: 'flex-end', backgroundColor: '#DCF8C6' },
  bot: { alignSelf: 'flex-start', backgroundColor: '#F1F0F0' },
  msgText: { fontSize: 16 },
  image: { width: 200, height: 200, marginTop: 8, borderRadius: 8 }
});
