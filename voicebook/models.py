from django.db import models

class VoiceRecording(models.Model):
    audio_file = models.FileField(upload_to='voice_recordings/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recording {self.id} - {self.created_at}"

class Record(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('INCOMPLETE', 'Incomplete'),
        ('COMPLETED', 'Completed'),
        ('ERROR', 'Error')
    ]
    
    TRANSACTION_TYPE_CHOICES = [
        ('SALE', 'Sale'),
        ('PURCHASE', 'Purchase'),
        ('RETURN', 'Return'),
        ('ADJUSTMENT', 'Adjustment')
    ]
        
    text = models.TextField()
    original_text = models.TextField(blank=True)  # Store original text in local language
    original_sound = models.ForeignKey(VoiceRecording, on_delete=models.CASCADE,null=True, blank=True)  # Store original text in local language
    original_language = models.CharField(max_length=10, blank=True)
    product_name = models.CharField(max_length=255, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    missing_info = models.JSONField(null=True, blank=True)  # Store missing information
    audio_file = models.FileField(upload_to='audio_uploads/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, default='SALE')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Record {self.id} - {self.status} - {self.created_at}"

