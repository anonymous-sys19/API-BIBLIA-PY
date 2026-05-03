# 📘 Información de la Base de Datos Bíblica
Archivo analizado: **rvr1960.sqlite**

## 📂 Tablas encontradas
```
book       metadata   testament  verse    
```

## 🧩 Estructura de cada tabla

### 🔸 Tabla: `book`
```
0|id|INTEGER|1||1
1|testament_id|INTEGER|0||0
2|name|VARCHAR(50)|0||0
3|abbreviation|VARCHAR(5)|0||0
```

### 🔸 Tabla: `metadata`
```
0|key|VARCHAR(255)|1||1
1|value|VARCHAR(255)|0||0
```

### 🔸 Tabla: `testament`
```
0|id|INTEGER|1||1
1|name|VARCHAR(50)|0||0
```

### 🔸 Tabla: `verse`
```
0|id|INTEGER|1||1
1|book_id|INTEGER|0||0
2|chapter|INTEGER|0||0
3|verse|INTEGER|0||0
4|text|TEXT|0||0
```

