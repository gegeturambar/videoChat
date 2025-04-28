# VideoQA

![License](https://img.shields.io/badge/license-MIT-green.svg)

VideoQA est une application web permettant d'interroger le contenu d'une vidéo via une interface conversationnelle intelligente.
Le système extrait la transcription audio de la vidéo (grâce à Whisper), génère des embeddings pour le contexte, et répond à vos questions en s'appuyant sur ce contexte enrichi.

## 🚀 Fonctionnalités principales

- **Transcription automatique** : Extraction de la piste audio et transcription avec Whisper.
- **Indexation intelligente** : Génération d'embeddings pour permettre la recherche contextuelle dans la vidéo.
- **Questions-Réponses** : Posez des questions sur la vidéo, obtenez des réponses précises grâce à un système RAG (Retrieval Augmented Generation).
- **Interface moderne** : Frontend React avec TailwindCSS pour une expérience fluide.
- **Backend Python** : API FastAPI pour l'extraction, la gestion des embeddings et l'orchestration des réponses.

## 🛠️ Stack technique

- **Frontend** : React, TailwindCSS
- **Backend** : Python, FastAPI
- **Transcription** : OpenAI Whisper
- **RAG & IA** : OpenAI, Anthropic, etc.
- **Base de données vectorielle** : Pour le stockage des embeddings

## ⚡ Exemple de flux

1. **Upload ou lien vidéo** (YouTube, fichier, etc.)
2. **Transcription automatique** (Whisper)
3. **Indexation et embeddings**
4. **Question utilisateur** (interface chat)
5. **Recherche contextuelle et génération de réponse**

## 📦 Installation rapide

```bash
git clone https://github.com/gegeturambar/videoChat.git
cd videoChat
# Suivre les instructions backend et frontend dans leurs dossiers respectifs
```

## 📚 Cas d'usage

- Résumer une vidéo longue
- Retrouver un passage précis à partir d'une question
- Générer des FAQ à partir d'un contenu vidéo

## ⚠️ Limitations & considérations

- Les vidéos longues peuvent nécessiter un temps de traitement important.
- L'utilisation d'APIs IA (Whisper, OpenAI) peut engendrer des coûts.
- Respectez les droits d'auteur lors de l'utilisation de contenus protégés. 