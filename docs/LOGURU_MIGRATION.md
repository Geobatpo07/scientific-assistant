# Migration vers Loguru

## 🎯 Résumé

Le système de logging a été migré de **structlog** vers **Loguru** pour une meilleure simplicité et performance.

## ✅ Changements effectués

### 1. Dépendances
**Avant** : `structlog>=23.2.0`  
**Après** : `loguru>=0.7.0`

### 2. Fichier `app/utils/logger.py`

Complètement réécrit pour utiliser Loguru avec une configuration optimale :

```python
from app.utils.logger import get_logger

# Utilisation identique à avant
logger = get_logger(__name__)
logger.info("Mon message")
```

## 🌟 Avantages de Loguru

### 1. **Plus simple**
```python
# Avant (structlog)
logger.info("message", key1="value1", key2="value2")

# Après (Loguru) - identique !
logger.info("message", key1="value1", key2="value2")
```

### 2. **Meilleure gestion des exceptions**
```python
try:
    dangerous_operation()
except Exception:
    logger.exception("Erreur détectée")  # Trace complète automatique
```

### 3. **Rotation automatique des logs**
- Nouveau fichier chaque jour à minuit
- Conservation pendant 30 jours
- Compression automatique en ZIP
- Format: `scientific_assistant_YYYY-MM-DD.log`

### 4. **Logs colorés en console**
Format lisible avec couleurs :
```
2026-01-01 19:49:17 | INFO     | module:function - Mon message
```

### 5. **Thread-safe par défaut**
- `enqueue=True` : tous les logs sont thread-safe
- Pas de problème avec les applications multi-threads

## 📝 Configuration

### Console
- **Format** : Coloré et lisible avec timestamp, niveau, module et message
- **Niveau** : Défini par `settings.LOG_LEVEL`
- **Sortie** : `stdout`

### Fichiers
1. **Log texte**
   - Fichier : `logs/scientific_assistant_{date}.log`
   - Rotation : Chaque jour à minuit
   - Rétention : 30 jours
   - Compression : ZIP

2. **Log JSON** (si `settings.LOG_FORMAT == "json"`)
   - Fichier : `logs/scientific_assistant_{date}.json`
   - Format : JSON structuré
   - Même rotation et rétention

## 🚀 Utilisation

### Basique
```python
from app.utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("Message de debug")
logger.info("Message d'information")
logger.warning("Avertissement")
logger.error("Erreur")
logger.critical("Erreur critique")
```

### Avec contexte
```python
logger.info("Action utilisateur", user_id=123, action="login")
# Output: ... - Action utilisateur
```

### Exceptions
```python
try:
    result = 1 / 0
except Exception:
    logger.exception("Erreur de division")
    # Affiche automatiquement la stack trace complète
```

### Logger nommé
```python
# Pour des modules spécifiques
module_logger = get_logger("mon_module")
module_logger.info("Message du module")
```

## 🔧 Fonctionnalités avancées

### Ajout de champs personnalisés
```python
logger.bind(request_id="abc123").info("Traitement requête")
```

### Logging conditionnel
```python
logger.opt(lazy=True).debug("Heavy computation: {result}", result=lambda: expensive_call())
```

### Catch decorator
```python
from loguru import logger

@logger.catch
def my_function():
    # Les exceptions sont automatiquement loggées
    return 1 / 0
```

### Performance
```python
# Désactiver temporairement
logger.disable("mon_module")

# Réactiver
logger.enable("mon_module")
```

## 📊 Formats de logs

### Console (par défaut)
```
2026-01-01 19:49:17 | INFO     | app.vectorstore.chroma:search - Searching for: query...
```

### Fichier texte
```
2026-01-01 19:49:17 | INFO     | app.vectorstore.chroma:search:105 - Searching for: query...
```

### JSON (si activé)
```json
{
    "text": "Searching for: query...",
    "record": {
        "elapsed": {"repr": "0:00:00.123", "seconds": 0.123},
        "level": {"name": "INFO", "no": 20},
        "time": {"repr": "2026-01-01 19:49:17", "timestamp": 1735761557.0}
    }
}
```

## ♻️ Compatibilité

✅ **Code existant** : Fonctionne sans modification  
✅ **get_logger()** : Même interface  
✅ **Niveaux de log** : Identiques (DEBUG, INFO, WARNING, ERROR, CRITICAL)  
✅ **setup_logging()** : Conservée (mais optionnelle)

## 🔍 Comparaison

| Fonctionnalité | structlog | Loguru |
|---------------|-----------|---------|
| Configuration | Complexe (50+ lignes) | Simple (20 lignes) |
| Rotation | Manuel | Automatique |
| Compression | Non | Oui (ZIP) |
| Couleurs | Avec config | Par défaut |
| Thread-safe | Config requise | Par défaut |
| Exceptions | Basique | Excellente |
| Performance | Bonne | Excellente |
| API | Verbeux | Fluide |

## 📦 Dépendances supplémentaires

- `loguru>=0.7.0` - Logger principal
- `win32-setctime>=1.2.0` - Support Windows pour les timestamps (auto-installé)

## 🧪 Tests

Lancez le test pour vérifier :
```bash
uv run python tests/test_loguru.py
```

Résultat attendu :
- ✅ Messages colorés dans la console
- ✅ Fichier de log créé dans `logs/`
- ✅ Exceptions bien formatées

## 📖 Documentation officielle

- [Loguru Documentation](https://loguru.readthedocs.io/)
- [GitHub](https://github.com/Delgan/loguru)

## 💡 Bonnes pratiques

1. **Toujours utiliser get_logger()**
   ```python
   logger = get_logger(__name__)
   ```

2. **Logger les exceptions avec .exception()**
   ```python
   except Exception:
       logger.exception("Erreur détectée")
   ```

3. **Utiliser des f-strings ou format**
   ```python
   logger.info(f"Processing {count} items")
   # ou
   logger.info("Processing {} items", count)
   ```

4. **Ne pas logger en boucle intensive**
   ```python
   # ❌ Mauvais
   for i in range(1000000):
       logger.debug(f"Item {i}")
   
   # ✅ Bon
   logger.info(f"Processing {len(items)} items")
   ```

## ✨ Nouveautés disponibles

Grâce à Loguru, vous avez maintenant accès à :

- 🎨 **Logs colorés** automatiquement
- 🔄 **Rotation quotidienne** automatique
- 📦 **Compression ZIP** des anciens logs
- 🧹 **Nettoyage automatique** (30 jours)
- 🔒 **Thread-safety** par défaut
- 📊 **Format JSON** optionnel
- 🎯 **Meilleure gestion** des exceptions
- ⚡ **Meilleures performances**

---

**Date de migration** : 1er janvier 2026  
**Status** : ✅ Migration complète et testée
