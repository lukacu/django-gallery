# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Image', fields ['album', 'title_slug']
        db.delete_unique('gallery_image', ['album_id', 'title_slug'])

        # Removing unique constraint on 'Album', fields ['parent', 'title_slug']
        db.delete_unique('gallery_album', ['parent_id', 'title_slug'])

        # Deleting field 'Album.rght'
        db.delete_column('gallery_album', 'rght')

        # Deleting field 'Album.parent'
        db.delete_column('gallery_album', 'parent_id')

        # Deleting field 'Album.tags'
        db.delete_column('gallery_album', 'tags')

        # Deleting field 'Album.lft'
        db.delete_column('gallery_album', 'lft')

        # Deleting field 'Album.level'
        db.delete_column('gallery_album', 'level')

        # Deleting field 'Album.cover'
        db.delete_column('gallery_album', 'cover_id')

        # Deleting field 'Album.tree_id'
        db.delete_column('gallery_album', 'tree_id')

        # Deleting field 'Album.order'
        db.delete_column('gallery_album', 'order')

        # Changing field 'Image.album'
        db.alter_column('gallery_image', 'album_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gallery.Album']))

    def backwards(self, orm):
        
        # Removing unique constraint on 'Image', fields ['title_slug']
        db.delete_unique('gallery_image', ['title_slug'])

        # Removing unique constraint on 'Album', fields ['title_slug']
        db.delete_unique('gallery_album', ['title_slug'])

        # User chose to not deal with backwards NULL issues for 'Album.rght'
        raise RuntimeError("Cannot reverse this migration. 'Album.rght' and its values cannot be restored.")

        # Adding field 'Album.parent'
        db.add_column('gallery_album', 'parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', null=True, to=orm['gallery.Album'], blank=True), keep_default=False)

        # Adding field 'Album.tags'
        db.add_column('gallery_album', 'tags', self.gf('tagging.fields.TagField')(default=''), keep_default=False)

        # User chose to not deal with backwards NULL issues for 'Album.lft'
        raise RuntimeError("Cannot reverse this migration. 'Album.lft' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Album.level'
        raise RuntimeError("Cannot reverse this migration. 'Album.level' and its values cannot be restored.")

        # Adding field 'Album.cover'
        db.add_column('gallery_album', 'cover', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cover', null=True, to=orm['gallery.Image'], blank=True), keep_default=False)

        # User chose to not deal with backwards NULL issues for 'Album.tree_id'
        raise RuntimeError("Cannot reverse this migration. 'Album.tree_id' and its values cannot be restored.")

        # Adding field 'Album.order'
        db.add_column('gallery_album', 'order', self.gf('django.db.models.fields.CharField')(default='', max_length=2), keep_default=False)

        # Adding unique constraint on 'Album', fields ['parent', 'title_slug']
        db.create_unique('gallery_album', ['parent_id', 'title_slug'])

        # Changing field 'Image.album'
        db.alter_column('gallery_image', 'album_id', self.gf('mptt.fields.TreeForeignKey')(to=orm['gallery.Album']))

        # Adding unique constraint on 'Image', fields ['album', 'title_slug']
        db.create_unique('gallery_image', ['album_id', 'title_slug'])


    models = {
        'gallery.album': {
            'Meta': {'object_name': 'Album'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title_slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        },
        'gallery.image': {
            'Meta': {'ordering': "['-date_added']", 'object_name': 'Image'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gallery.Album']"}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'enable_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'original_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'tags': ('tagging.fields.TagField', [], {'default': "''"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'thumbnail_parameters': ('gallery.fields.ThumbnailParametersField', [], {'max_length': '32', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title_slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['gallery']
