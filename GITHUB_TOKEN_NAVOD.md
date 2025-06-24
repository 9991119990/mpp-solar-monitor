# Jak vytvořit GitHub Personal Access Token (2024)

## 🔑 Aktuální cesta k Personal Access Tokens

GitHub změnil rozhraní. Zde je **aktuální postup**:

### Krok 1: Přejděte do Settings
1. **Klikněte na svůj avatar** v pravém horním rohu
2. Vyberte **"Settings"** (ne Repository settings!)

### Krok 2: Najděte Developer settings  
1. V levém menu **scrollujte úplně dolů**
2. Najděte sekci **"Developer settings"** (je skoro na konci)
3. Klikněte na **"Developer settings"**

### Krok 3: Personal access tokens
1. V levém menu klikněte **"Personal access tokens"**
2. Vyberte **"Tokens (classic)"**
3. Klikněte **"Generate new token"**
4. Vyberte **"Generate new token (classic)"**

### Krok 4: Konfigurace tokenu
1. **Note**: `MPP Solar Monitor Upload`
2. **Expiration**: `90 days` (nebo podle potřeby)
3. **Scopes**: Zaškrtněte **✅ repo** (poskytne přístup k repozitářům)
4. Klikněte **"Generate token"**

### Krok 5: Zkopírujte token
⚠️ **DŮLEŽITÉ**: Token se zobrazí pouze jednou!
- Zkopírujte token a uložte si ho
- Vypadá něco jako: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## 🚀 Použití tokenu

Když vás GitHub vyzve k zadání hesla, **použijte token místo hesla**:

```bash
Username: vase_github_jmeno
Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 🛠️ Alternativní řešení

### Možnost A: GitHub CLI (nejjednodušší)
```bash
# Instalace GitHub CLI
sudo apt install gh

# Přihlášení (otevře webový prohlížeč)
gh auth login

# Automatické vytvoření a upload repozitáře
gh repo create mpp-solar-monitor --public --source=. --remote=origin --push
```

### Možnost B: SSH klíče
1. Vygenerujte SSH klíč:
```bash
ssh-keygen -t ed25519 -C "vas@email.com"
```
2. Přidejte do GitHub: **Settings → SSH and GPG keys**
3. Použijte SSH URL místo HTTPS

### Možnost C: Jednoduché řešení
Pokud GitHub CLI nefunguje, můžete:
1. **Vytvořit repozitář na GitHub.com** ručně
2. **Upload files** - kliknout na "uploading an existing file"
3. **Přetáhnout všechny soubory** do prohlížeče

## 📍 Přesná cesta (2024):

```
GitHub.com → 
Váš avatar (pravý horní roh) → 
Settings → 
(scroll dolů na konec levého menu) → 
Developer settings → 
Personal access tokens → 
Tokens (classic) → 
Generate new token (classic)
```

## 🎯 Nejrychlejší řešení:

**Přímý link**: https://github.com/settings/tokens

---

**💡 Tip**: Pokud stále nemůžete najít Developer settings, možná máte firemní GitHub účet s omezeními. V tom případě použijte GitHub CLI nebo upload přes webové rozhraní.