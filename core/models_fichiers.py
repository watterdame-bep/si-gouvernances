"""
Modèle pour la gestion des fichiers attachés aux projets
"""
from django.db import models
from django.utils import timezone
import os


class FichierProjet(models.Model):
    """Fichiers attachés à un projet"""
    
    projet = models.ForeignKey(
        'Projet',
        on_delete=models.CASCADE,
        related_name='fichiers'
    )
    
    fichier = models.FileField(
        upload_to='projets/fichiers/%Y/%m/',
        verbose_name='Fichier'
    )
    
    nom_original = models.CharField(
        max_length=255,
        verbose_name='Nom du fichier'
    )
    
    taille = models.BigIntegerField(
        default=0,
        verbose_name='Taille (octets)'
    )
    
    type_mime = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Type MIME'
    )
    
    date_ajout = models.DateTimeField(
        default=timezone.now,
        verbose_name='Date d\'ajout'
    )
    
    ajoute_par = models.ForeignKey(
        'Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        related_name='fichiers_ajoutes',
        verbose_name='Ajouté par'
    )
    
    class Meta:
        db_table = 'core_fichierprojet'
        verbose_name = 'Fichier de projet'
        verbose_name_plural = 'Fichiers de projet'
        ordering = ['-date_ajout']
    
    def __str__(self):
        return f"{self.nom_original} - {self.projet.nom}"
    
    def get_extension(self):
        """Retourne l'extension du fichier"""
        return os.path.splitext(self.nom_original)[1].lower()
    
    def get_taille_formatee(self):
        """Retourne la taille formatée"""
        taille = self.taille
        for unite in ['o', 'Ko', 'Mo', 'Go']:
            if taille < 1024.0:
                return f"{taille:.1f} {unite}"
            taille /= 1024.0
        return f"{taille:.1f} To"
    
    def get_icone(self):
        """Retourne l'icône FontAwesome selon le type de fichier"""
        ext = self.get_extension()
        
        # Documents
        if ext in ['.pdf']:
            return 'fa-file-pdf text-red-600'
        elif ext in ['.doc', '.docx']:
            return 'fa-file-word text-blue-600'
        elif ext in ['.xls', '.xlsx']:
            return 'fa-file-excel text-green-600'
        elif ext in ['.ppt', '.pptx']:
            return 'fa-file-powerpoint text-orange-600'
        
        # Images
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
            return 'fa-file-image text-purple-600'
        
        # Archives
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return 'fa-file-archive text-yellow-600'
        
        # Code
        elif ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php']:
            return 'fa-file-code text-indigo-600'
        
        # Texte
        elif ext in ['.txt', '.md', '.log']:
            return 'fa-file-alt text-gray-600'
        
        # Défaut
        else:
            return 'fa-file text-gray-500'
