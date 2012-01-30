# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Album.weight'
        db.delete_column('gallery_album', 'weight')

        # Changing field 'Image.album'
        db.alter_column('gallery_image', 'album_id', self.gf('mptt.fields.TreeForeignKey')(to=orm['gallery.Album']))


    def backwards(self, orm):
        
        # Adding field 'Album.weight'
        db.add_column('gallery_album', 'weight', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True), keep_default=False)

        # Changing field 'Image.album'
        db.alter_column('gallery_image', 'album_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gallery.Album']))


    models = {
        'gallery.album': {
            'Meta': {'unique_together': "(('title_slug', 'parent'),)", 'object_name': 'Album'},
            'cover': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cover'", 'null': 'True', 'to': "orm['gallery.Image']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'order': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['gallery.Album']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {'default': "''"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title_slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'gallery.image': {
            'Meta': {'ordering': "['-date_added']", 'unique_together': "(('title_slug', 'album'),)", 'object_name': 'Image'},
            'album': ('mptt.fields.TreeForeignKey', [], {'to': "orm['gallery.Album']"}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'enable_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'original_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'tags': ('tagging.fields.TagField', [], {'default': "''"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title_slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['gallery']
