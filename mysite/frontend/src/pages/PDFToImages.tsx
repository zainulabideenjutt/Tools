import { useState } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Typography,
  Alert,
  AlertTitle,
  Grid,
  IconButton,
} from '@mui/material'
import { useDropzone } from 'react-dropzone'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import DeleteIcon from '@mui/icons-material/Delete'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import axios from 'axios'

interface FileWithPreview extends File {
  preview?: string
}

const PDFToImages = () => {
  const [file, setFile] = useState<FileWithPreview | null>(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [convertedImages, setConvertedImages] = useState<string[]>([])

  const onDrop = (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const newFile = Object.assign(acceptedFiles[0], {
        preview: URL.createObjectURL(acceptedFiles[0]),
      })
      setFile(newFile)
      setConvertedImages([])
      setError('')
      setSuccess(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    multiple: false,
  })

  const removeFile = () => {
    if (file?.preview) {
      URL.revokeObjectURL(file.preview)
    }
    setFile(null)
    setConvertedImages([])
    setError('')
    setSuccess(false)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a PDF file')
      return
    }

    setError('')
    setSuccess(false)
    setLoading(true)

    const formData = new FormData()
    formData.append('document', file)

    try {
      const response = await axios.post('/api/pdf-to-images-converter', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setConvertedImages(response.data.images || [])
      setSuccess(true)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'An error occurred while processing your request'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ py: 4 }}>
      <Typography variant="h1" sx={{ mb: 4, textAlign: 'center' }}>
        PDF to Images Converter
      </Typography>
      <Typography variant="h2" sx={{ mb: 6, textAlign: 'center' }}>
        Convert PDF Pages to Images
      </Typography>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          {!file && (
            <Box
              {...getRootProps()}
              sx={{
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'grey.300',
                borderRadius: 1,
                p: 3,
                mb: 3,
                textAlign: 'center',
                cursor: 'pointer',
                '&:hover': {
                  borderColor: 'primary.main',
                },
              }}
            >
              <input {...getInputProps()} />
              <CloudUploadIcon
                sx={{ fontSize: 48, color: 'primary.main', mb: 2 }}
              />
              <Typography variant="h6" gutterBottom>
                {isDragActive
                  ? 'Drop the PDF here'
                  : 'Drag & drop a PDF file here, or click to select'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Supported format: PDF
              </Typography>
            </Box>
          )}

          {file && (
            <Box sx={{ mb: 3 }}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  p: 2,
                  border: '1px solid',
                  borderColor: 'grey.300',
                  borderRadius: 1,
                }}
              >
                <PictureAsPdfIcon sx={{ mr: 2, color: 'primary.main' }} />
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="subtitle1">{file.name}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </Typography>
                </Box>
                <IconButton onClick={removeFile} size="small">
                  <DeleteIcon />
                </IconButton>
              </Box>
            </Box>
          )}

          <Button
            variant="contained"
            fullWidth
            size="large"
            disabled={loading || !file}
            onClick={handleSubmit}
            sx={{ mb: 3 }}
          >
            {loading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              'Convert to Images'
            )}
          </Button>

          {success && convertedImages.length > 0 && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" gutterBottom>
                Converted Images
              </Typography>
              <Grid container spacing={2}>
                {convertedImages.map((imageUrl, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card>
                      <CardContent>
                        <img
                          src={imageUrl}
                          alt={`Page ${index + 1}`}
                          style={{ width: '100%', height: 'auto' }}
                        />
                        <Button
                          href={imageUrl}
                          download={`page_${index + 1}.png`}
                          variant="outlined"
                          fullWidth
                          sx={{ mt: 1 }}
                        >
                          Download
                        </Button>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {success && (
            <Alert severity="success" sx={{ mt: 2 }}>
              <AlertTitle>Success</AlertTitle>
              Your PDF has been converted to images successfully!
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <AlertTitle>Error</AlertTitle>
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>
    </Box>
  )
}

export default PDFToImages