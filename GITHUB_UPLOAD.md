# Jak nahrát projekt na GitHub

## 📋 Krok za krokem

### 1. Vytvoření GitHub repozitáře

1. Jděte na **https://github.com**
2. Přihlaste se ke svému účtu
3. Klikněte na **"New repository"** (zelené tlačítko)
4. Zadejte název: `mpp-solar-monitor`
5. Přidejte popis: `MPP Solar PIP5048MG monitoring system with Home Assistant integration`
6. Vyberte **Public** nebo **Private** podle potřeby
7. **NEVYBÍREJTE** "Initialize with README" (už máme vlastní)
8. Klikněte **"Create repository"**

### 2. Propojení lokálního repozitáře

Po vytvoření repozitáře GitHub zobrazí instrukce. Použijte druhou možnost "push an existing repository":

```bash
cd /home/dell/mpp-solar-monitor

# Přidejte GitHub jako remote origin
git remote add origin https://github.com/VASE_UZIVATELSKE_JMENO/mpp-solar-monitor.git

# Nastavte main jako výchozí branch
git branch -M main

# Pushněte kód na GitHub
git push -u origin main
```

⚠️ **Nahraďte `VASE_UZIVATELSKE_JMENO` vaším skutečným GitHub usernamem!**

### 3. Autentifikace

GitHub vás vyzve k autentifikaci. Máte několik možností:

#### Možnost A: Personal Access Token (doporučeno)
1. Jděte na **GitHub → Settings → Developer settings → Personal access tokens**
2. Klikněte **"Generate new token (classic)"**
3. Vyberte scope: `repo` (full control of private repositories)
4. Zkopírujte token a použijte místo hesla

#### Možnost B: GitHub CLI
```bash
# Nainstalujte GitHub CLI
sudo apt install gh

# Přihlaste se
gh auth login

# Pushněte repozitář
gh repo create mpp-solar-monitor --public --source=. --remote=origin --push
```

### 4. Ověření úspěchu

Po úspěšném upload navštivte:
```
https://github.com/VASE_UZIVATELSKE_JMENO/mpp-solar-monitor
```

Měli byste vidět všechny soubory včetně README.md.

## 🔄 Budoucí aktualizace

Pro přidání nových změn:
```bash
cd /home/dell/mpp-solar-monitor

# Přidejte změny
git add .
git commit -m "Popis změn"
git push
```

## 🏷️ Vytvoření release

1. Na GitHubu jděte do **Releases → Create a new release**
2. Tag: `v1.0.0`
3. Title: `MPP Solar Monitor v1.0.0`
4. Popis: `První stable verze s kompletní HA integrací`
5. Publikujte release

## ✨ Bonus: Pěkný README

Váš README.md už obsahuje:
- ✅ Odznaky a emoji
- ✅ Ukázky kódu
- ✅ Screenshots (text-based)
- ✅ Instalační instrukce
- ✅ Troubleshooting

GitHub to automaticky zobrazí na hlavní stránce repozitáře!

---

**🎯 Po uploadu budete mít krásný, profesionální GitHub repozitář s kompletní dokumentací!**