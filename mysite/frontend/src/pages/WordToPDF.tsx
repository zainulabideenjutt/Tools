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
  IconButton,
} from '@mui/material'
import { useDropzone } from 'react-dropzone'
import DescriptionIcon from '@mui/icons-material/Description'
import DeleteIcon from '@mui/icons-material/Delete'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import axios from 'axios'
import DownloadIcon from '@mui/icons-material/Download'

interface FileWithPreview extends File {
  preview?: string
}

const WordToPDF = () => {
  const [file, setFile] = useState<FileWithPreview | null>(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)

  const onDrop = (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const newFile = Object.assign(acceptedFiles[0], {
        preview: URL.createObjectURL(acceptedFiles[0]),
      })
      setFile(newFile)
      setError('')
      setSuccess(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': [
        '.docx',
      ],
    },
    multiple: false,
  })

  const removeFile = () => {
    if (file?.preview) {
      URL.revokeObjectURL(file.preview)
    }
    setFile(null)
    setError('')
    setSuccess(false)
    setPdfUrl(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a Word document')
      return
    }

    setError('')
    setSuccess(false)
    setLoading(true)
    setPdfUrl(null)

    const formData = new FormData()
    formData.append('document', file)

    try {
      const response = await axios.post('/api/word-to-pdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setSuccess(true)
      setPdfUrl(response.data.converted_pdf)
      console.log(response.data.converted_pdf)
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

  const handleDownload = async () => {
    if (!pdfUrl) return
    
    try {
      const response = await axios.get(pdfUrl, {
        responseType: 'blob'
      })
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'converted.pdf')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError('Failed to download the PDF')
    }
  }

  return (
    <Box sx={{ py: 4 }}>
      <Typography variant="h1" sx={{ mb: 4, textAlign: 'center' }}>
        Word to PDF Converter
      </Typography>
      <Typography variant="h2" sx={{ mb: 6, textAlign: 'center' }}>
        Convert Word Documents to PDF
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
                  ? 'Drop the document here'
                  : 'Drag & drop a Word document here, or click to select'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Supported formats: DOC, DOCX
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
                <DescriptionIcon sx={{ mr: 2, color: 'primary.main' }} />
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
              'Convert to PDF'
            )}
          </Button>

          {success && (
            <Alert severity="success" sx={{ mt: 2 }}>
              <AlertTitle>Success</AlertTitle>
              Your document has been converted to PDF successfully!
            </Alert>
          )}

          {pdfUrl && (
            <Box sx={{ mt: 3 }}>
              <Box sx={{ mb: 2, display: 'flex', justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={handleDownload}
                >
                  Download PDF
                </Button>
              </Box>
              <Box sx={{ 
                width: '100%', 
                height: '500px', 
                border: '1px solid rgba(0, 0, 0, 0.12)', 
                borderRadius: 1 
              }}>
                <iframe
                  src={pdfUrl}
                  style={{
                    width: '100%',
                    height: '100%',
                    border: 'none',
                  }}
                  title="PDF Preview"
                />
              </Box>
            </Box>
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

export default WordToPDF