# VolkConverter

A multimedia GUI converter for audio assets extracted from game archives and containers. Specially designed to automate the decompilation, conversion, and organization of audio files.

## Key Features

* **Multi-format Support:** Compatible with `.WEM`, `.BNK`, `.PCK`, `.FSB`, `.USM`, and `.HCA` formats.
* **Container Parsing:** Automatic ripping and extraction of `RIFF` / `WAVEfmt` audio streams directly from `.PCK` files.
* **Dictionary Integration:** Supports mapping original names from hash dictionaries via configuration files (`.json`, `.csv`, `.txt`).
* **Smart Sorting:** Automatically categorizes converted files into folders (`MUSIC`, `VOICE`, `SFX`) based on track duration analysis and name prefixes.
* **Watchdog (Autoscan):** Real-time monitoring mode that tracks a target folder and converts new files on the fly.
* **Build Comparer:** A built-in tool to compare the file structures of two different versions to track modified, added, or deleted audio assets.
* **Signature Scanner:** A manual tool to search for and dump arbitrary HEX or text signatures from binary files.
* **Built-in Player:** Quick preview and playback of converted audio directly within the interface.
* **FFmpeg Audio Processing:** EBU R128 loudness normalization, forced 5.1 to stereo downmixing, silence trimming, and metadata tagging.

---

## Requirements & Environment Setup

To ensure the application runs correctly, you need to install the Python dependencies and prepare the external command-line utilities.

### 1. Installing Python Libraries

Before running the script, install the required modules using the following command:

```bash
pip install -r requirements.txt

```

### 2. External Engines

The converter relies on third-party utilities to decode and encode audio streams. These are included alongside the script, but **they must be unpacked/unzipped separately**.

* `vgmstream-cli.exe` — used for decoding game audio formats.
* `ffmpeg.exe` — used for conversion and final audio post-processing.

---

## Using Name Dictionaries

To automatically replace generic hashed filenames (e.g., `10234567.wem`) with proper names, load a dictionary file via the UI:

* **JSON:** Key-value format (`{"10234567": "bgm_mondstadt_theme"}`)
* **CSV:** Two columns without headers (`10234567,bgm_mondstadt_theme`)
* **TXT:** Line-by-line using an equal sign (`10234567=bgm_mondstadt_theme`)





# VolkConverter 

Мультимедийный графический конвертер аудиоресурсов из игровых архивов и контейнеров. Разработан специально для автоматизации декомпиляции, конвертации и упорядочивания аудиофайлов.

## Основной функционал

* **Мультиформатность:** Поддержка форматов `.WEM`, `.BNK`, `.PCK`, `.FSB`, `.USM` и `.HCA`.
* **Парсинг контейнеров:** Автоматический риппинг и извлечение аудиопотоков `RIFF` / `WAVEfmt` прямо из файлов `.PCK`.
* **Интеграция словарей:** Поддержка подстановки оригинальных названий из хэш-словарей через файлы конфигурации (`.json`, `.csv`, `.txt`).
* **Умная сортировка:** Автоматическое распределение сконвертированных файлов по категориям (`MUSIC`, `VOICE`, `SFX`) на основе анализа длительности треков и префиксов в именах.
* **Watchdog (Автоскан):** Режим реального времени для автоматического мониторинга целевой папки и конвертации новых файлов на лету.
* **Сравнение билдов:** Встроенный инструмент сопоставления файловых структур двух разных версий для отслеживания измененных, добавленных или удаленных аудиоресурсов.
* **Сигнатурный сканер:** Ручной инструмент для поиска и дампа произвольных HEX/текстовых сигнатур из бинарных файлов.
* **Встроенный плеер:** Быстрое прослушивание результатов конвертации без выхода из интерфейса.
* **Обработка звука через FFmpeg:** EBU R128 нормализация громкости, принудительный даунмикс из 5.1 в стерео, обрезка тишины в хвостах и запись метаданных.

---

## Требования и подготовка окружения

Для корректной работы приложения необходимо установить зависимости Python и подготовить внешние консольные утилиты.

### 1. Установка библиотек Python

Перед запуском скрипта установите необходимые модули командой:

```bash
pip install -r requirements.txt

```

### 2. Внешние движки (Engines)

Конвертер использует сторонние утилиты для декодирования и кодирования аудиопотоков. **Они идут сразу вместе с самим скриптом, но их необходимо разархивировать отдельно.**

* `vgmstream-cli.exe` — для декодирования игровых аудиоформатов.
* `ffmpeg.exe` — для конвертации и финальной обработки звука.

---

## Использование словарей имён

Для автоматической замены безликих хэш-имен файлов (например, `10234567.wem`) на нормальные названия, загрузите файл словаря через интерфейс:

* **JSON:** Формат ключ-значение (`{"10234567": "bgm_mondstadt_theme"}`)
* **CSV:** Две колонки без заголовков (`10234567,bgm_mondstadt_theme`)
* **TXT:** Построчно через знак равенства (`10234567=bgm_mondstadt_theme`)

