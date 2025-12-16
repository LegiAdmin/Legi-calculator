from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Legislation, TaxBracket, Allowance, UsufructScale, SimulationScenario, Donation

class TaxBracketInline(admin.TabularInline):
    model = TaxBracket
    extra = 0
    fields = ('relationship', 'min_amount', 'max_amount', 'rate', 'summary')
    readonly_fields = ('summary',)
    ordering = ('relationship', 'min_amount')
    verbose_name = "📊 Tranche fiscale"
    verbose_name_plural = "📊 Tranches fiscales (Barème progressif)"
    
    def summary(self, obj):
        max_display = f"{obj.max_amount:,.0f}€" if obj.max_amount else "∞"
        return format_html(
            '<span style="color: #0066cc; font-weight: bold;">{} - {} : {}%</span>',
            f"{obj.min_amount:,.0f}€",
            max_display,
            f"{obj.rate * 100:.1f}"
        )
    summary.short_description = "Résumé de la tranche"

class AllowanceInline(admin.TabularInline):
    model = Allowance
    extra = 0
    fields = ('relationship', 'amount', 'formatted_amount')
    readonly_fields = ('formatted_amount',)
    verbose_name = "💶 Abattement fiscal"
    verbose_name_plural = "💶 Abattements fiscaux (Réductions d'impôt)"
    
    def formatted_amount(self, obj):
        return format_html(
            '<strong style="color: #00aa00;">{:,.0f}€</strong>',
            obj.amount
        )
    formatted_amount.short_description = "Montant formaté"

class UsufructScaleInline(admin.TabularInline):
    model = UsufructScale
    extra = 0
    fields = ('max_age', 'rate', 'rate_display')
    readonly_fields = ('rate_display',)
    ordering = ('max_age',)
    verbose_name = "📐 Barème d'usufruit"
    verbose_name_plural = "📐 Barèmes d'usufruit (Art. 669 CGI)"
    
    def rate_display(self, obj):
        return f"{obj.rate * 100:.0f}%"
    rate_display.short_description = "Taux (%)"

@admin.register(Legislation)
class LegislationAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'is_active_badge', 'rule_counts')
    list_filter = ('year', 'is_active')
    search_fields = ('name',)
    ordering = ('-year', '-is_active')
    
    fieldsets = (
        ('📋 Informations générales', {
            'fields': ('name', 'year', 'is_active'),
            'description': '''
                <div style="background: #e3f2fd; padding: 15px; border-left: 4px solid #2196F3; margin: 10px 0;">
                    <h3 style="margin-top: 0;">💡 Comment utiliser cette page :</h3>
                    <p><strong>Législation</strong> : Ensemble de règles fiscales applicables pour une année donnée.</p>
                    <ul>
                        <li><strong>Une seule législation active</strong> : Le moteur utilise automatiquement la législation marquée comme "active"</li>
                        <li><strong>Année</strong> : Année de référence (ex: 2025)</li>
                    </ul>
                    <p style="margin-bottom: 0;"><em>Les règles ci-dessous sont automatiquement appliquées lors des simulations.</em></p>
                </div>
            '''
        }),
    )
    
    inlines = [AllowanceInline, TaxBracketInline, UsufructScaleInline]
    
    class Media:
        css = {
            'all': ['admin/css/forms.css']
        }
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">✓ ACTIVE</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    is_active_badge.short_description = "Statut"
    
    def rule_counts(self, obj):
        allowances = obj.allowances.count()
        brackets = obj.tax_brackets.count()
        scales = obj.usufruct_scales.count()
        return format_html(
            '💶 {} abattements • 📊 {} tranches • 📐 {} barèmes usufruit',
            allowances, brackets, scales
        )
    rule_counts.short_description = "Règles configurées"

@admin.register(TaxBracket)
class TaxBracketAdmin(admin.ModelAdmin):
    list_display = ('legislation', 'relationship', 'bracket_range', 'rate_display')
    list_filter = ('legislation', 'relationship')
    ordering = ('legislation', 'relationship', 'min_amount')
    search_fields = ('legislation__name',)
    
    fieldsets = (
        ('📊 Tranche fiscale', {
            'fields': ('legislation', 'relationship'),
        }),
        ('💰 Montants et taux', {
            'fields': ('min_amount', 'max_amount', 'rate'),
            'description': 'Définissez la plage de montants et le taux applicable. Laissez max_amount vide pour "∞".'
        }),
    )
    
    def bracket_range(self, obj):
        max_display = f"{obj.max_amount:,.0f}€" if obj.max_amount else "∞"
        return f"{obj.min_amount:,.0f}€ - {max_display}"
    bracket_range.short_description = "Tranche"
    
    def rate_display(self, obj):
        return format_html(
            '<strong style="color: #dc3545;">{:.2f}%</strong>',
            obj.rate * 100
        )
    rate_display.short_description = "Taux"

@admin.register(Allowance)
class AllowanceAdmin(admin.ModelAdmin):
    list_display = ('legislation', 'relationship', 'amount_display')
    list_filter = ('legislation', 'relationship')
    ordering = ('legislation', 'relationship')
    search_fields = ('legislation__name',)
    
    fieldsets = (
        ('💶 Abattement fiscal', {
            'fields': ('legislation', 'relationship', 'amount'),
            'description': '''
                <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 10px 0;">
                    <h3 style="margin-top: 0;">💶 Qu'est-ce qu'un abattement ?</h3>
                    <p><strong>L'abattement</strong> est une réduction fiscale qui diminue la base taxable d'un héritier.</p>
                    <p><strong>Exemple</strong> : Un enfant hérite de 150 000€. Avec un abattement de 100 000€ :</p>
                    <ul>
                        <li>Part brute : 150 000€</li>
                        <li>Abattement : -100 000€</li>
                        <li><strong>Base taxable : 50 000€</strong> (c'est sur ce montant que l'impôt sera calculé)</li>
                    </ul>
                    <p><strong>Valeurs courantes (2025)</strong> :</p>
                    <ul>
                        <li>Enfants/Parents : 100 000€</li>
                        <li>Frères/Sœurs : 15 932€</li>
                        <li>Neveux/Nièces : 7 967€</li>
                        <li>Conjoint/Partenaire PACS : Exonération totale</li>
                    </ul>
                </div>
            '''
        }),
    )
    
    def amount_display(self, obj):
        return format_html(
            '<strong style="color: #28a745; font-size: 1.1em;">{:,.0f}€</strong>',
            obj.amount
        )
    amount_display.short_description = "Montant"

@admin.register(UsufructScale)
class UsufructScaleAdmin(admin.ModelAdmin):
    list_display = ('legislation', 'age_range', 'rate_display')
    list_filter = ('legislation',)
    ordering = ('legislation', 'max_age')
    
    fieldsets = (
        ('📐 Barème d\'usufruit', {
            'fields': ('legislation', 'max_age', 'rate'),
            'description': 'Barème fiscal de valorisation de l\'usufruit selon l\'âge (Art. 669 CGI).'
        }),
    )
    
    def age_range(self, obj):
        return f"< {obj.max_age} ans"
    age_range.short_description = "Âge"
    
    def rate_display(self, obj):
        return format_html(
            '<strong style="color: #fd7e14;">{:.0f}%</strong>',
            obj.rate * 100
        )
    rate_display.short_description = "Taux"

@admin.register(SimulationScenario)
class SimulationScenarioAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('🧪 Scénario de test', {
            'fields': ('name', 'description'),
        }),
        ('📝 Données', {
            'fields': ('input_data',),
            'description': 'JSON du scénario de simulation.'
        }),
        ('📅 Métadonnées', {
            'fields': ('created_at',),
        }),
    )
    
    def description_short(self, obj):
        if obj.description and len(obj.description) > 50:
            return obj.description[:50] + "..."
        return obj.description or "-"
    description_short.short_description = "Description"

# Personnalisation du site admin
admin.site.site_header = "🏛️ Succession Engine - Administration"
admin.site.site_title = "Succession Engine Admin"
admin.site.index_title = "Gestion du moteur de succession"
