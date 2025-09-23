# Configuración de AWS Textract para Extracción de Documentos

Este documento explica cómo configurar AWS Textract para habilitar la extracción de texto avanzada de documentos e imágenes.

## 🚀 ¿Qué es AWS Textract?

AWS Textract es un servicio de machine learning que extrae automáticamente texto, escritura a mano y datos de documentos escaneados. Va más allá del OCR tradicional al identificar, entender y extraer datos de formularios y tablas.

### Ventajas del Sistema Híbrido

- **📄 PDFs**: Textract → PyPDF2 (fallback)
- **📸 Imágenes**: Textract → Mensaje informativo (sin Textract)
- **📝 Texto plano**: Decodificación directa
- **📋 Word**: python-docx

## 🔧 Configuración

### 1. Crear una cuenta AWS

1. Ve a [AWS Console](https://aws.amazon.com/console/)
2. Crea una cuenta si no tienes una
3. Inicia sesión en la consola

### 2. Configurar IAM (Permisos)

1. Ve a **IAM** en la consola AWS
2. Crea un nuevo usuario:
   - Nombre: `textract-user` (o el que prefieras)
   - Tipo de acceso: **Programmatic access**
3. Asigna permisos:
   - Opción 1 (Recomendada): Crear política personalizada
   - Opción 2 (Más simple): Usar `AmazonTextractFullAccess`

#### Política Personalizada (Recomendada)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "textract:DetectDocumentText",
                "textract:AnalyzeDocument"
            ],
            "Resource": "*"
        }
    ]
}
```

### 3. Obtener Credenciales

Después de crear el usuario, obtendrás:
- **Access Key ID**: `AKIAIOSFODNN7EXAMPLE`
- **Secret Access Key**: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

⚠️ **IMPORTANTE**: Guarda estas credenciales de forma segura. No las compartas ni las subas a repositorios.

### 4. Configurar Variables de Entorno

#### En Desarrollo (Local)

Crea un archivo `.env` en el directorio `backend/`:

```env
# AWS Configuration for Textract
AWS_ACCESS_KEY_ID=tu_access_key_id_aqui
AWS_SECRET_ACCESS_KEY=tu_secret_access_key_aqui
AWS_REGION=us-east-1

# Optional: S3 configuration (si también usas S3)
AWS_S3_BUCKET_NAME=tu-bucket-name
```

#### En Producción (Render)

1. Ve a tu servicio en Render
2. Ve a **Environment**
3. Agrega las variables:
   - `AWS_ACCESS_KEY_ID`: tu_access_key_id_aqui
   - `AWS_SECRET_ACCESS_KEY`: tu_secret_access_key_aqui
   - `AWS_REGION`: us-east-1

## 📊 Verificación

### 1. Health Check

Visita: `https://tu-backend.com/documents/extraction-status`

Deberías ver:

```json
{
  "status": "operational",
  "extraction_service": {
    "textract_available": true,
    "aws_credentials": true,
    "supported_formats": {
      "text": ["txt", "md"],
      "pdf": ["pdf"],
      "word": ["docx", "doc"],
      "images": ["png", "jpg", "jpeg", "tiff", "bmp", "webp"]
    },
    "extraction_methods": {
      "aws_textract": "Available",
      "pypdf2": "Available",
      "python_docx": "Available",
      "text_decode": "Available"
    }
  },
  "message": "AWS Textract available"
}
```

### 2. Prueba de Extracción

Usa el endpoint: `POST /documents/test-extraction`

```bash
curl -X POST "https://tu-backend.com/documents/test-extraction" \
  -F "file=@mi_documento.pdf" \
  -F "use_textract=true"
```

## 💰 Costos

### Precios de AWS Textract (2024)

- **DetectDocumentText**: $0.0015 por página
- **AnalyzeDocument**: $0.050 por página
- **Nivel gratuito**: 1,000 páginas gratis el primer mes

### Ejemplo de Costos

Para un uso típico de 1,000 páginas al mes:
- Solo texto: ~$1.50/mes
- Con análisis de formularios: ~$50/mes

## 🔄 Fallback sin Textract

Si no configuras AWS Textract, el sistema seguirá funcionando:

- **PDFs**: Se usará PyPDF2
- **Imágenes**: Se mostrará un mensaje informativo
- **Word/Texto**: Funcionará normalmente

## 🛠️ Troubleshooting

### Error: "AWS credentials not found"

**Solución**: Verifica que las variables de entorno estén configuradas correctamente.

### Error: "AccessDeniedException"

**Solución**: Verifica que el usuario IAM tenga los permisos correctos para Textract.

### Error: "InvalidParameterException"

**Solución**: Verifica que el archivo no exceda 10MB y esté en un formato soportado.

### Textract no extrae texto

**Posibles causas**:
- Imagen de muy baja calidad
- Texto muy pequeño o borroso
- Formato de imagen no compatible
- Documento dañado

## 📚 Recursos Adicionales

- [AWS Textract Documentation](https://docs.aws.amazon.com/textract/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Textract Pricing](https://aws.amazon.com/textract/pricing/)

## 🔒 Seguridad

1. **Nunca hardcodees credenciales** en el código
2. **Usa IAM roles** en lugar de usuarios cuando sea posible
3. **Rota las credenciales** regularmente
4. **Monitorea el uso** para detectar actividad inusual
5. **Usa políticas mínimas** (principio de menor privilegio)

---

¡Con esta configuración, tu sistema legal podrá procesar tanto documentos digitales como fotos de documentos físicos! 📸⚖️
