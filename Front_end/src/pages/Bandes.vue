<template>
  <div class="bande-root">
    <nav class="bande-tabs">
      <div class="logo">
        <img src="../assets/icons/LOGO.svg" alt="Logo" />
        <span>AVIPRO</span>
      </div>

      <div class="tabs">
        <span class="logo-section">
          <img src="../assets/icons/dashboard.svg"/>
          <button :class="{ active: activeTab === 'dashboard' }" @click="selectTab('dashboard')">
            Dashboard
          </button>
        </span>

        <span class="logo-section">
          <img src="../assets/icons/consommation.svg"/>
          <button :class="{ active: activeTab === 'consommation' }" @click="selectTab('consommation')">
            Consommation
          </button>
        </span>

        <span class="logo-section">
          <img src="../assets/icons/predictions.svg"/>
          <button :class="{ active: activeTab === 'predictions' }" @click="selectTab('predictions')">
            Predictions
          </button> 
        </span>

        

        <span class="logo-section">
          <img src="../assets/icons/sante.svg"/>
          <button :class="{ active: ['sante','traitements','animaux'].includes(activeTab) }" @click="selectTab('sante')" class="taches">Sante</button>
        </span>

        <span class="logo-section">
          <img src="../assets/icons/finances.svg"/>
          <button
            :class="{ active: activeTab === 'finances' }"
            @click="selectTab('finances')"
          >
            Finances
          </button>
        </span>

        <span class="logo-section">
          <img src="../assets/icons/infos.svg"/>
          <button
            :class="{ active: activeTab === 'infos' }"
            @click="selectTab('infos')"
          >
            Infos
          </button>
        </span>

        <span class="logo-section">
          <img src="../assets/icons/aide.svg"/>
          <button
            :class="{ active: activeTab === 'aide' }"
            @click="selectTab('aide')"
          >
            Aide
          </button>
        </span>
      </div>

      <div class="sidebar-footer">
        <div class="sidebar-actions">
          <button class="back-home" @click="goHome">
            <img src="../assets/icons/exit.svg" alt="Accueil" />
          </button>
          <span class="settings" @click="openSettings">
            <i class="fas fa-cog"></i>
          </span>
        </div>
      </div>
    </nav>

      <main class="main-section">

        <!-- Header -->
        <header class="bande-header">
        <div class="header-main">
          <div class="header-title">
            <p class="header-kicker">Tableau de bord</p>
            <h1>{{ band?.nom || 'Bande' }}</h1>
            <div class="header-chips">
              <span class="chip ghost">Statut: {{ band?.statut || '—' }}</span>
              <span class="chip ghost">Arrivée: {{ band?.date_arrivee || '—' }}</span>
              <span class="chip ghost">Âge: {{ animalAgeWeeks || currentProductionWeek }} sem</span>
              <span class="chip ghost">Effectif: {{ band?.nombre_initial || 0 }}</span>
            </div>
          </div>
        </div>

        <div class="header-actions">
          <div class="search">
            <input
              class="search"
              v-model="searchQuery"
              @input="updateSearchResults"
              @keydown="handleSearchKeydown"
              @focus="updateSearchResults"
              @blur="closeSearch"
              placeholder="Rechercher (onglet, action...)"
            />
            <img src="../assets/icons/search.svg">
            <ul class="search-suggestions" v-if="searchResults.length">
              <li
                v-for="(item, idx) in searchResults"
                :key="item.key"
                :class="{ active: idx === searchFocusedIndex }"
                @mousedown.prevent="executeSearchResult(item)"
              >
                <div class="search-line">
                  <span class="search-label">{{ item.label }}</span>
                  <span class="search-type">{{ item.type }}</span>
                </div>
                <div v-if="item.hint" class="search-hint">{{ item.hint }}</div>
              </li>
            </ul>
          </div>
          <button class="ai" :class="{ active: activeTab === 'chatbot' }"
            @click="selectTab('chatbot')"></button>
        </div>
      </header>

        <!-- Dashboard Tab -->
        <section
          v-if="activeTab === 'dashboard'"
          class="tab-panel dashboard-panel modern-dashboard"
        >
          <div class="dash-hero">
            <div class="hero-left">
              <p class="eyebrow">Vue bande</p>
              <h2>{{ band?.nom || 'Bande' }}</h2>
              <div class="hero-chips">
                <span class="pill ghost">Statut: {{ band?.statut || '—' }}</span>
                <span class="pill ghost">Arrivée: {{ band?.date_arrivee || '—' }}</span>
                <span class="pill ghost">Durée: {{ band?.duree_jours || 0 }} j ({{ durationWeeks }} sem)</span>
              </div>
              <div class="hero-metrics">
                <div class="metric">
                  <span>Survie</span>
                  <strong>{{ survivalPerformance }}%</strong>
                  <small>{{ survivorsCount }}/{{ band?.nombre_initial || 0 }} oiseaux</small>
                </div>
                <div class="metric">
                  <span>IC</span>
                  <strong>{{ consumptionIndex }}</strong>
                  <small>Coût/poule cumulé</small>
                </div>
                <div class="metric">
                  <span>Coûts engagés</span>
                  <strong>{{ formatCurrencyFCFA(totalCostsAll, 0) }}</strong>
                  <small>Aliment + dépenses + soins</small>
                </div>
                <div class="metric">
                  <span>Âge</span>
                  <strong>{{ currentProductionWeek }} sem</strong>
                  <small>{{ ageLabel }}</small>
                </div>
              </div>
            </div>
            <div class="hero-right">
              <PerformanceGauge :score="performancePercent" />
              <div class="hero-legend">
                <span class="dot good"></span><small>Survie</small>
                <span class="dot warn"></span><small>Gains & Conso</small>
              </div>
              <button v-if="serverPerformance" class="btn-small" @click.stop="showBandPerfDetails">Détails perf</button>
            </div>
          </div>

          <div class="dash-grid primary">
            <div class="dash-card span-2">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Poids</p>
                  <h3>Évolution vs référence</h3>
                </div>
                <span class="chip ghost">Sem {{ currentProductionWeek }}</span>
              </div>
              <AnimalWeightChart
                :labels="weightChartLabels"
                :actual="weightActualSeries"
                :ref-low="weightRefLowSeries"
                :ref-high="weightRefHighSeries"
                height="240"
              />
            </div>

            <div class="dash-card span-1">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Aliment</p>
                  <h3>Volumes hebdo</h3>
                </div>
                <span class="chip">{{ feedPerBird }} kg/poule</span>
              </div>
              <FeedVolumeChart :band="band" :consommations="consommations" height="240" />
            </div>

            <div class="dash-card span-1">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Eau</p>
                  <h3>Volumes hebdo</h3>
                </div>
                <span class="chip ghost">{{ waterPerBird }} L/poule</span>
              </div>
              <WaterVolumeChart :band="band" :consommations="consommations" height="240" />
            </div>

            <div class="dash-card span-1 compact">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Population</p>
                  <h3>Survie & pertes</h3>
                </div>
              </div>
              <PopulationDonut :band="band" :survival="survivalPerformance" :deaths="totalAnimalDeaths" height="180" />
              <div class="stat-list">
                <div class="row"><span>Arrivés</span><strong>{{ band?.nombre_initial || 0 }}</strong></div>
                <div class="row"><span>Restants</span><strong>{{ survivorsCount }}</strong></div>
                <div class="row"><span>Mortalité</span><strong>{{ mortalityRate }}%</strong></div>
              </div>
            </div>

            <div class="dash-card span-1 compact">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Coûts</p>
                  <h3>Top postes</h3>
                </div>
              </div>
              <CostBreakdownChart :consommations="consommations" height="200" />
              <div class="stat-list">
                <div class="row"><span>Coût total alim</span><strong>{{ formatCurrencyFCFA(totalCost, 0) }}</strong></div>
                <div class="row"><span>Charges santé</span><strong>{{ formatCurrencyFCFA(totalTreatmentCost, 0) }}</strong></div>
                <div class="row"><span>Autres dépenses</span><strong>{{ formatCurrencyFCFA(totalExpensesElementaires, 0) }}</strong></div>
              </div>
            </div>

            <div class="dash-card span-2">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Performance</p>
                  <h3>Aliment & cumul</h3>
                </div>
              </div>
              <PerformanceChart :band="band" :consommations="consommations" height="240" />
            </div>

            <div class="dash-card span-2">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Gains</p>
                  <h3>Observé vs référence</h3>
                </div>
              </div>
              <GainsLineChart
                :labels="gainsComputed.labels"
                :actual="gainsComputed.actual"
                :reference="gainsComputed.reference"
                height="240"
              />
            </div>

            <div class="dash-card span-1 compact">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Cumul coûts</p>
                  <h3>Waterfall</h3>
                </div>
              </div>
              <WaterfallCostChart :consommations="consommations" :band="band" :predictions="predictions" :optimalPrediction="optimalPrediction" :mode="'dashboard'" :revenueCurrent="gainsComputed.cumActual" />
            </div>

            <div class="dash-card span-1 compact">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Coûts hebdo</p>
                  <h3>Réel vs réf</h3>
                </div>
              </div>
              <ConsumptionCostChart
                :consommations="consommations"
                :band="band"
                :consumption-reference="consumptionReference"
              />
            </div>
          </div>

          <div class="dash-grid primary calendar-row">
            <div class="dash-card span-4 calendar-card">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Calendrier</p>
                  <h3>Période de bande</h3>
                </div>
                <span class="chip ghost">{{ bandDateRange.durationLabel }}</span>
              </div>
              <div class="calendar-meta">
                <span class="pill subtle">Début: {{ bandDateRange.startLabel }}</span>
                <span class="pill subtle">Fin: {{ bandDateRange.endLabel }}</span>
                <span class="pill subtle">Cycle: {{ durationWeeks }} sem</span>
              </div>
              <div class="calendar-body">
                <div class="calendar-months">
                  <div
                    v-for="month in bandCalendarMonths"
                    :key="month.monthLabel"
                    class="month-block"
                  >
                    <div class="month-header">{{ month.monthLabel }}</div>
                    <div class="calendar-grid">
                      <div class="calendar-day header" v-for="day in ['Lu','Ma','Me','Je','Ve','Sa','Di']" :key="day">{{ day }}</div>
                      <div
                        v-for="cell in month.cells"
                        :key="cell.key"
                        class="calendar-day"
                        :class="{
                          empty: cell.empty,
                          range: cell.inRange,
                          start: cell.isStart,
                          end: cell.isEnd,
                          event: cell.events && cell.events.length
                        }"
                      >
                        <span class="day-number" v-if="!cell.empty">{{ cell.day }}</span>
                        <div v-if="cell.events && cell.events.length" class="event-dots">
                          <span v-for="(ev, idx) in cell.events.slice(0,3)" :key="idx" class="dot" :title="ev.label"></span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="calendar-agenda">
                  <div class="card-head small">
                    <div>
                      <p class="eyebrow">Agenda</p>
                      <h3>Dates clés</h3>
                    </div>
                  </div>
                  <KeyDatesTimeline :events="dashboardKeyEvents" :limit="6" />
                </div>
              </div>
            </div>
          </div>

          <div class="dash-grid secondary">
            <div class="dash-card span-2">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Mortalité</p>
                  <h3>Observée vs bornes</h3>
                </div>
              </div>
              <AnimalMortalityChart
                :labels="animalLineLabels"
                :series="animalMortalitySeries"
                :ref-low="animalRefLowSeries"
                :ref-high="animalRefHighSeries"
                height="220"
              />
            </div>

            <div class="dash-card span-2">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Poids hebdo</p>
                  <h3>Observation vs réf</h3>
                </div>
              </div>
              <AnimalWeightChart
                :labels="weightChartLabels"
                :actual="weightActualSeries"
                :ref-low="weightRefLowSeries"
                :ref-high="weightRefHighSeries"
                height="220"
              />
            </div>

            <div class="dash-card span-1 compact">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Survie</p>
                  <h3>Vue rapide</h3>
                </div>
              </div>
              <AnimalWeeklyPie :survived="survivorsCount" :deaths="totalAnimalDeaths" />
              <div class="stat-list">
                <div class="row"><span>Dernière semaine</span><strong>{{ lastAnimalWeek || '—' }}</strong></div>
                <div class="row"><span>Dernier poids</span><strong>{{ animalLastWeight?.value || '—' }} kg</strong></div>
                <div class="row"><span>Conseils</span><strong>{{ animalAdvice.length }}</strong></div>
              </div>
            </div>

            <div class="dash-card span-1 compact">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Dépenses</p>
                  <h3>Répartition</h3>
                </div>
              </div>
              <ExpenseDonutChart :expenses="expenseRecords" height="180" />
              <div class="stat-list">
                <div class="row"><span>Total suivi</span><strong>{{ formatCurrencyFCFA(totalExpensesElementaires, 0) }}</strong></div>
                <div class="row"><span>Postes saisis</span><strong>{{ expenseRecords.length }}</strong></div>
              </div>
            </div>

            <div class="dash-card span-2 compact">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Flux</p>
                  <h3>Dernières consommations</h3>
                </div>
              </div>
              <ul class="mini-list">
                <li v-for="c in recentConsumptions" :key="c.id || c.date">
                  <div class="mini-top">
                    <span class="pill subtle">{{ formatDate(c.date) }}</span>
                    <strong>{{ formatNumber(c.kg || 0) }} kg</strong>
                  </div>
                  <div class="mini-bottom">{{ c.type || 'Aliment' }} • {{ formatCurrencyFCFA(c.cout || 0) }}</div>
                </li>
                <li v-if="!recentConsumptions.length" class="muted">Aucune consommation saisie.</li>
              </ul>
            </div>
          </div>

          <div class="dash-grid secondary">
            <div class="dash-card span-4">
              <div class="card-head">
                <div>
                  <p class="eyebrow">Santé</p>
                  <h3>Usage des traitements</h3>
                </div>
                <span class="chip ghost">{{ treatmentRecords.length }} enregs.</span>
              </div>
              <TreatmentUsageChart :treatments="treatmentRecords" height="220" />
              <div class="stat-list">
                <div class="row"><span>Coût total</span><strong>{{ formatCurrencyFCFA(totalTreatmentCost, 0) }}</strong></div>
                <div class="row"><span>Produits distincts</span><strong>{{ treatmentProductCount }}</strong></div>
                <div class="row"><span>Jours cumulés</span><strong>{{ totalTreatmentDays }}</strong></div>
              </div>
            </div>
          </div>

          <div class="dashboard-insights compact">
            <div
              v-for="insight in dashboardInsights"
              :key="insight.title"
              class="insight-card"
              :class="insight.tone"
            >
              <div class="insight-header">
                <span class="pill subtle">{{ insight.title }}</span>
                <span class="insight-value">{{ insight.value }}</span>
              </div>
              <p class="insight-desc">{{ insight.detail }}</p>
            </div>
          </div>
        </section>

        <!-- Consommation Tab -->
        <section
          v-if="activeTab === 'consommation'"
          class="tab-panel consommation-panel"
        >
          <h2>Consommations</h2>
          <div class="consumption-rules">
            <strong>Règles d'ajout</strong>
            <ul>
              <li>Une seule consommation par semaine (calculée depuis la date d'arrivée).</li>
              <li>Le coût total est calculé automatiquement si un prix unitaire est renseigné.</li>
              <li>L'eau (L) est suivie en plus du poids d'aliment.</li>
            </ul>
          </div>

          <form @submit.prevent="addConsumption" class="consumption-form">
            <div class="form-hints">
              <span class="pill subtle">1. Choisir la semaine</span>
              <span class="pill subtle">2. Saisir kg &amp; L</span>
              <span class="pill subtle">3. Prix unitaire (pas 25 FCFA)</span>
            </div>
            <div class="form-grid">
              <label>
                <span>Semaine de production</span>
                <select v-model.number="consumptionForm.semaine_production" required :disabled="!band">
                  <option value="">Sélectionner une semaine</option>
                  <option
                    v-for="week in weekOptions"
                    :key="week.week"
                    :value="week.week"
                    :disabled="week.disabled"
                    :class="{ 'disabled-week': week.disabled }"
                  >
                    S{{ week.week }}<span v-if="week.disabled"> (remplie)</span>
                  </option>
                </select>
              </label>
              <label>
                <span>Type d'aliment</span>
                <select v-model="consumptionForm.type" required>
                  <option value="">Choisir un type</option>
                  <option value="Démarrage">Démarrage</option>
                  <option value="Croissance">Croissance</option>
                  <option value="Finition">Finition</option>
                  <option value="Autre">Autre</option>
                </select>
              </label>
              
              <label>
                <span>Quantité (kg)</span>
                <input
                  type="number"
                  v-model.number="consumptionForm.kg"
                  placeholder="Kg"
                  step="0.01"
                  required
                  @input="updateCostPreview"
                />
              </label>
              <label>
                <span>PU aliment (FCFA/kg)</span>
                <input
                  type="number"
                  v-model.number="consumptionForm.prix_unitaire"
                  placeholder="Ex: 450"
                  step="25"
                  min="0"
                  @input="updateCostPreview"
                />
              </label>
              <label>
                <span>Eau (L)</span>
                <input
                  type="number"
                  v-model.number="consumptionForm.eau_litres"
                  placeholder="Litres d'eau"
                  step="0.01"
                  min="0"
                  @input="updateCostPreview"
                />
              </label>
              <label>
                <span>PU eau (FCFA/L)</span>
                <input
                  type="number"
                  v-model.number="consumptionForm.prix_eau_unitaire"
                  placeholder="Ex: 25"
                  step="25"
                  min="0"
                  @input="updateCostPreview"
                />
              </label>
            </div>
            <div class="cost-preview" v-if="consumptionFormCostPreview > 0">
              <strong>Coût estimé:</strong> {{ formatCurrencyFCFA(consumptionFormCostPreview) }}
            </div>
            <div class="consumption-actions">
              <button class="btn" type="submit" :disabled="!consumptionForm.semaine_production">
                {{ editingConsumptionId ? 'Mettre à jour' : 'Ajouter' }}
              </button>
              <button
                v-if="editingConsumptionId"
                class="btn secondary"
                type="button"
                @click="resetConsumptionForm"
              >
                Annuler
              </button>
            </div>
            <div class="consumption-totals">
              <div>
                <span>Total consommations actuelles:</span>
                <strong>{{ formatCurrencyFCFA(totalCost) }}</strong>
              </div>
              <div v-if="consumptionFormCostPreview > 0">
                <span>Coût estimé saisie en cours:</span>
                <strong>{{ formatCurrencyFCFA(consumptionFormCostPreview) }}</strong>
              </div>
            </div>
          </form>

          <div class="consumption-summary">
            <h3>Suivi hebdomadaire (sur la durée de la bande)</h3>
            <table class="weekly-consumption-table">
              <thead>
                <tr>
                  <th>Semaine</th>
                  <th>Aliment (kg)</th>
                  <th>Eau (L)</th>
                  <th>PU alim (FCFA/kg)</th>
                  <th>PU eau (FCFA/L)</th>
                  <th>Coût total (FCFA)</th>
                  <th class="actions-col">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in weeklyConsumptionRows" :key="row.week">
                  <td>S{{ row.week }}</td>
                  <td>{{ row.aliment }}</td>
                  <td>{{ row.eau }}</td>
                  <td>{{ row.prixUnitaire }}</td>
                  <td>{{ row.prixEau }}</td>
                  <td>{{ row.cout }}</td>
                  <td class="table-actions">
                    <button class="icon-btn" title="Modifier" @click="editWeek(row)">✏️</button>
                    <button class="icon-btn danger" title="Supprimer" @click="deleteWeek(row)">🗑️</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="consumption-dates" v-if="consumptionPeriod.start">
            <div>
              <strong>Début suivi:</strong> {{ consumptionPeriod.start }}
            </div>
            <div>
              <strong>Fin prévue:</strong> {{ consumptionPeriod.end }}
            </div>
          </div>

          <div class="consumption-analytics">
            <div class="charts-stack">
              <div class="chart-card narrow">
                <h3>Historique des consommations</h3>
                <ConsumptionHistoryChart :consommations="consommations" :band="band" />
              </div>
              <div class="chart-card narrow">
                <h3>Coût hebdomadaire (FCFA)</h3>
                <ConsumptionCostChart
                  :consommations="consommations"
                  :band="band"
                  :consumption-reference="consumptionReference"
                />
              </div>
            </div>
            <div class="side-stack">
              <div class="chart-card performance-card">
                <h3>Performance conso / coût</h3>
                <PerformanceGauge :score="consumptionPerformance.overall" />
                <div class="performance-breakdown">
                  <span>Conso vs réf: {{ formatPercent(consumptionPerformance.consumption) }}</span>
                  <span>Coût vs réf: {{ formatPercent(consumptionPerformance.cost) }}</span>
                </div>
              </div>
              <div class="chart-card">
                <h3>Calendrier du mois</h3>
                <div class="month-calendar" v-if="monthCalendar">
                  <div class="month-header">{{ monthCalendar.monthLabel }}</div>
                  <div class="month-grid">
                    <div class="day head" v-for="d in ['L','M','M','J','V','S','D']" :key="d">{{ d }}</div>
                    <div
                      v-for="(cell, idx) in monthCalendar.cells"
                      :key="idx"
                      :class="[
                        'day',
                        {
                          empty: !cell.date,
                          today: cell.isToday,
                          start: cell.isStart,
                          end: cell.isEnd,
                          'week-range': cell.isWeekRange,
                          'week-start': cell.isWeekStart,
                          'week-end': cell.isWeekEnd
                        }
                      ]"
                    >
                      <span v-if="cell.date">{{ cell.day }}</span>
                    </div>
                  </div>
                  <div class="month-legend">
                    <span class="legend-dot start"></span> Début semaine (dernière conso)
                    <span class="legend-dot end"></span> Fin semaine (dernière conso)
                    <span class="legend-dot today"></span> Aujourd'hui
                    <span class="legend-dot week-range"></span> Semaine conso (dernière remplie)
                  </div>
                </div>
              </div>
            </div>
          </div>

            <div class="advice-card" v-if="lastWeekAdvice.length">
              <div class="advice-header">
                <h3>Alertes & conseils (dernière semaine)</h3>
                <span class="pill subtle">Référence vs réel</span>
              </div>
              <div class="advice-list">
                <div
                  v-for="(advice, idx) in lastWeekAdvice"
                  :key="idx"
                  :class="['advice', advice.level]"
                >
                  {{ advice.text }}
                </div>
              </div>
            </div>
            <div class="advice-card muted" v-else>
              <h3>Alertes & conseils</h3>
              <p class="muted">Ajoutez une consommation pour obtenir des recommandations.</p>
            </div>
        </section>

        <!-- Predictions Tab -->
        <section
          v-if="activeTab === 'predictions'"
          class="tab-panel predictions-panel"
        >
          <h2>Predictions</h2>

          <div v-if="predictionErrorMsg" class="alert warning">
            {{ predictionErrorMsg }}
          </div>

          <div v-else-if="!predictions.length" class="muted" style="margin: 8px 0 12px;">
            Aucune prédiction pour l'instant. Ajoutez des données (poids ou consommations) puis cliquez sur Générer.
          </div>
          
          <div class="prediction-controls">
            <div class="control-card">
              <div class="control-head">
                <span class="eyebrow">Horizon</span>
                <p>Choisissez la durée de projection</p>
              </div>
              <div class="option-pills">
                <button type="button" :class="{ active: predictionDays==='7' }" @click="predictionDays='7'">7 jours</button>
                <button type="button" :class="{ active: predictionDays==='14' }" @click="predictionDays='14'">14 jours</button>
                <button type="button" :class="{ active: predictionDays==='30' }" @click="predictionDays='30'">30 jours</button>
              </div>
            </div>

            <div class="control-card action-card">
              <div class="control-head">
                <span class="eyebrow">Lancer</span>
                <p>Générer les prévisions</p>
              </div>
              <button @click="generatePredictions" class="btn-primary">Générer</button>
            </div>
          </div>

          <div class="prediction-charts">
            <PredictionCharts :predictions="predictions" />
          </div>

          <div class="predictions-table">
            <h3>Détail des prédictions</h3>
            <table>
              <thead>
                <tr>
                  <th>Jour</th>
                  <th>Date</th>
                  <th>Poids (kg)</th>
                  <th>Consom. (kg)</th>
                  <th>Coût (FCFA)</th>
                  <th>Survie (%)</th>
                  <th>Gains (FCFA)</th>
                  <th>Marge (FCFA)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in predictions" :key="p.jour">
                  <td>J+{{ p.jour }}</td>
                  <td>{{ p.date }}</td>
                  <td>{{ p.poids.toFixed(2) }}</td>
                  <td>{{ p.consommation.toFixed(1) }}</td>
                  <td>{{ formatCurrencyFCFA(p.cout) }}</td>
                  <td>{{ p.taux_survie.toFixed(1) }}%</td>
                  <td>{{ formatCurrencyFCFA(p.valeur) }}</td>
                  <td :class="getMarginClass(p.marge)">{{ formatCurrencyFCFA(p.marge) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="prediction-summary">
            <div class="summary-card">
              <h4>Résumé</h4>
              <div class="summary-content">
                <div class="summary-item">
                  <span>Gain total estimé:</span>
                  <strong :class="getProfitClass(totalPredictedProfit)">
                    {{ formatCurrencyFCFA(totalPredictedProfit) }}
                  </strong>
                </div>
                <div class="summary-item">
                  <span>ROI estimé:</span>
                  <strong :class="getROIClass(roi)">
                    {{ roi.toFixed(1) }}%
                  </strong>
                </div>
                <div class="summary-item">
                  <span>Date optimale:</span>
                  <strong>{{ optimalSellingDate }}</strong>
                </div>
              </div>
            </div>
          </div>
        </section>


        <!-- Chatbot Tab -->
        <section v-if="activeTab === 'chatbot'" class="tab-panel chatbot-panel">
          <h2>Chatbot</h2>
          <div class="chatbox">
            <div class="chat-controls">
              <div class="chat-mode-head">
                <label>Mode IA</label>
                <span class="chat-mode-hint">Choisissez la source d'information</span>
              </div>
              <div class="chat-mode-pills">
                <button
                  type="button"
                  class="pill-btn"
                  :class="{ active: chatMode === 'data' }"
                  @click="chatMode = 'data'"
                >
                  Données internes
                </button>
                <button
                  type="button"
                  class="pill-btn"
                  :class="{ active: chatMode === 'hybrid' }"
                  @click="chatMode = 'hybrid'"
                >
                  Hybride
                </button>
                <button
                  type="button"
                  class="pill-btn"
                  :class="{ active: chatMode === 'web' }"
                  @click="chatMode = 'web'"
                >
                  Web uniquement
                </button>
                
                  <button 
                    @click="analyserElevage"
                    class="pill-btn"
                    :disabled="chatLoading"
                  >
                    📊 Analyser mon élevage
                  </button>
                
              </div>
            </div>
            <div class="messages">
              <div v-for="(m, i) in messages" :key="i" :class="['msg', m.from]">
                <span class="msg-text">{{ m.text }}</span>
                <button class="msg-close" aria-label="Fermer" @click="dismissChatMessage(i)">✕</button>
              </div>
              <div v-if="chatLoading" class="msg bot">…</div>
            </div>
            <form @submit.prevent="sendMessage" class="chat-form">
              <input
                v-model="chatInput"
                placeholder="Poser une question à l'IA"
              />
              <button class="btn" type="submit">Envoyer</button>
            </form>
          </div>
        </section>

        <!-- Infos Tab -->
        <section v-if="activeTab === 'infos'" class="tab-panel infos-panel">
          <div class="info-hero">
            <div>
              <p class="eyebrow">Fiche bande</p>
              <h2>{{ band?.nom_bande || 'Bande' }}</h2>
              <p class="muted">Race: {{ band?.race || '—' }} · Fournisseur: {{ band?.fournisseur || '—' }}</p>
              <div class="chips">
                <span class="pill subtle">Arrivée: {{ formatDate(band?.date_arrivee) || '—' }}</span>
                <span class="pill subtle">Durée prévue: {{ durationWeeks }} sem</span>
                <span class="pill subtle">Statut: {{ band?.statut || '—' }}</span>
              </div>
            </div>
            <div class="info-hero-cards">
              <div class="stat-card">
                <span class="label">Animaux initiaux</span>
                <span class="value">{{ band?.nombre_initial || 0 }}</span>
              </div>
              <div class="stat-card">
                <span class="label">Survivants</span>
                <span class="value">{{ survivorsCount }}</span>
              </div>
              <div class="stat-card">
                <span class="label">Mortalité</span>
                <span class="value">{{ mortalityRate }}%</span>
              </div>
              <div class="stat-card">
                <span class="label">Âge (sem)</span>
                <span class="value">{{ animalAgeWeeks }}</span>
              </div>
              <div class="stat-card">
                <span class="label">Dernier poids</span>
                <span class="value">{{ animalLastWeight?.value || band?.poids_moyen_initial || '—' }} kg</span>
              </div>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-card">
              <div class="info-card-header">
                <h3>Identification</h3>
              </div>
              <div class="info-rows">
                <div class="row"><span>Nom</span><strong>{{ band?.nom_bande || '—' }}</strong></div>
                <div class="row"><span>Race</span><strong>{{ band?.race || '—' }}</strong></div>
                <div class="row"><span>Lot / Fournisseur</span><strong>{{ band?.fournisseur || '—' }}</strong></div>
                <div class="row"><span>Statut</span><strong>{{ band?.statut || '—' }}</strong></div>
              </div>
            </div>

            <div class="info-card">
              <div class="info-card-header">
                <h3>Chronologie</h3>
              </div>
              <div class="info-rows">
                <div class="row"><span>Arrivée</span><strong>{{ formatDate(band?.date_arrivee) || '—' }}</strong></div>
                <div class="row"><span>Durée cible</span><strong>{{ durationWeeks }} sem ({{ band?.duree_jours || 42 }} jours)</strong></div>
                <div class="row"><span>Dernière saisie</span><strong>S{{ lastAnimalWeek || '—' }}</strong></div>
                <div class="row"><span>Prochaine semaine</span><strong>S{{ nextAnimalWeek }}</strong></div>
              </div>
            </div>

            <div class="info-card">
              <div class="info-card-header">
                <h3>Sanitaire</h3>
              </div>
              <div class="info-rows">
                <div class="row"><span>Morts cumulés</span><strong>{{ totalAnimalDeaths }}</strong></div>
                <div class="row"><span>Taux mortalité</span><strong>{{ mortalityRate }}%</strong></div>
                <div class="row"><span>Traitements (nb)</span><strong>{{ treatmentRecords.length }}</strong></div>
                <div class="row"><span>IC actuel</span><strong>{{ kpi?.consommation?.indice || consumptionIndex }}</strong></div>
              </div>
            </div>

            <div class="info-card">
              <div class="info-card-header">
                <h3>Finance express</h3>
              </div>
              <div class="info-rows">
                <div class="row"><span>Coûts engagés</span><strong>{{ formatCurrencyFCFA(totalCostsAll) }}</strong></div>
                <div class="row"><span>Coût alim/kg</span><strong>{{ formatCurrencyFCFA(kpi?.finances?.cout_alim_kg || 0) }}</strong></div>
                <div class="row"><span>Marge estimée</span><strong>{{ formatCurrencyFCFA(kpi?.finances?.marge_estimee || 0) }}</strong></div>
                <div class="row"><span>ROI estimé</span><strong>{{ (kpi?.finances?.roi || roi).toFixed ? (kpi?.finances?.roi || roi).toFixed(1) + '%' : roi.toFixed(1) + '%' }}</strong></div>
              </div>
            </div>
          </div>
        </section>

        <!-- Aide Tab -->
        <section v-if="activeTab === 'aide'" class="tab-panel aide-panel">
          <div class="help-hero">
            <div>
              <p class="eyebrow">Centre d'aide</p>
              <h2>Comment utiliser les onglets</h2>
              <p class="muted">Parcours guidé : découvrez quoi saisir, où regarder et quels indicateurs lire.</p>
            </div>
            <div class="help-actions">
              <button class="btn" @click="selectTab(selectedHelpSubTab)">Ouvrir l'onglet</button>
              <button class="btn secondary" @click="selectedHelpSubTab = 'dashboard'">Revenir au début</button>
            </div>
          </div>

          <div class="help-subtabs">
            <button
              v-for="section in helpSections"
              :key="section.key"
              :class="['help-subtab', { active: section.key === selectedHelpSubTab }]"
              @click="selectedHelpSubTab = section.key"
            >
              {{ section.label }}
            </button>
          </div>

          <div class="help-grid">
            <div class="help-card" v-for="card in currentHelpCards" :key="card.title">
              <div class="help-card-body">
                <p class="eyebrow">{{ card.badge }}</p>
                <h3>{{ card.title }}</h3>
                <p class="muted">{{ card.summary }}</p>
                <ul class="help-steps">
                  <li v-for="(step, idx) in card.steps" :key="idx">{{ step }}</li>
                </ul>
                <div class="help-actions">
                  <button class="btn secondary" @click="selectTab(card.targetTab)">Aller à {{ card.targetTab }}</button>
                </div>
              </div>
            </div>
          </div>
        </section>

        

        <!-- Animaux Tab -->
        <section v-if="activeTab === 'sante' && santeSubTab === 'animaux'" class="tab-panel animaux-panel">
          <!-- Sante subtab controls -->
        <div v-if="activeTab === 'sante'" class="sante-subtabs" style="margin-top: 16px; gap: 10px; margin-left: 20px;">
          <button  :class="['finance-subtab', { active: santeSubTab === 'animaux' }]" @click="santeSubTab = 'animaux'">Animaux</button>
          <button :class="['finance-subtab', { active: santeSubTab === 'traitements' }]" @click="santeSubTab = 'traitements'">Traitements</button>
        </div>

          <div class="animals-grid">
            
            
            <div class="card treatment-suggestions">
              
                <div>
                  <h2>Suivi animal</h2>
                  <p class="muted small">Enregistrer les informations de vos animaux </p>
                </div>
              <div class="animals-top">
                <div class="card animal-form-card">
                  <div class="card-header">
                    <h3>Saisie hebdomadaire</h3>
                    <span class="pill subtle">Semaine de production non bloquée par la conso</span>
                  </div>
                  <form class="animal-info-form" @submit.prevent="saveAnimalInfo">
                    <div class="form-row">
                      <label>
                        Semaine
                        <select v-model.number="animalInfoForm.semaine_production" required>
                          <option v-for="w in animalWeekOptions" :key="w.week" :value="w.week">
                            S{{ w.week }} <span v-if="w.hasInfo">(déjà saisie)</span>
                          </option>
                        </select>
                      </label>
                      <label>
                        Poids moyen (kg)
                        <input type="number" step="0.01" min="0" v-model.number="animalInfoForm.poids_moyen" />
                      </label>
                    </div>

                    <div class="form-row">
                      <label>
                        Morts semaine
                        <input type="number" min="0" v-model.number="animalInfoForm.morts_semaine" />
                      </label>
                      <label>
                        Animaux restants
                        <h2 style="color:grey" >{{animalInfoForm.animaux_restants-animalInfoForm.morts_semaine}} </h2>
                      </label>
                    </div>

                    <label class="full-row">
                      Note
                      <textarea rows="2" v-model="animalInfoForm.note" placeholder="Observation, symptômes, etc."></textarea>
                    </label>

                    <div class="animal-info-actions">
                      <button class="btn" type="submit">
                        {{ editingAnimalInfoId ? 'Mettre à jour' : 'Ajouter' }}
                      </button>
                      <button
                        v-if="editingAnimalInfoId"
                        class="btn secondary"
                        type="button"
                        @click="resetAnimalInfoForm"
                      >
                        Annuler
                      </button>
                    </div>
                  </form>
                </div>

                <div class="card animal-summary-card">
                <div class="card-header">
                  <div>
                    <h2>Suivi hebdomadaire des animaux</h2>
                    <p class="muted">La saisie poids/mortalité est indépendante des consommations.</p>
                  </div>
                  <div class="chip-group">
                    <span class="pill strong">Initial: {{ band?.nombre_initial || 0 }}</span>
                    <span class="pill danger">Morts cumulés: {{ totalAnimalDeaths }}</span>
                    <span class="pill success">Survivants: {{ survivorsCount }}</span>
                  </div>
                </div>

                <div class="animal-stats">
                  <div class="stat-block">
                    <span class="label">Race</span>
                    <span class="value">{{ band?.race || '—' }}</span>
                  </div>
                  <div class="stat-block">
                    <span class="label">Âge (sem.)</span>
                    <span class="value">{{ animalAgeWeeks }}</span>
                  </div>
                  <div class="stat-block">
                    <span class="label">Dernier poids</span>
                    <span class="value">{{ animalLastWeight && animalLastWeight.value !== null ? animalLastWeight.value + ' kg' : '—' }}</span>
                    <small v-if="animalLastWeight && animalLastWeight.week" class="muted">S{{ animalLastWeight.week }}</small>
                  </div>
                  <div class="stat-block">
                    <span class="label">Dernière semaine saisie</span>
                    <span class="value">S{{ lastAnimalWeek || '—' }}</span>
                  </div>
                  <div class="stat-block">
                    <span class="label">Performance survie</span>
                    <span class="value">{{ survivalPerformance.toFixed(0) }}%</span>
                  </div>
                  <div class="stat-block">
                    <span class="label">Prochaine semaine</span>
                    <span class="value">S{{ nextAnimalWeek }}</span>
                  </div>
                </div>
              </div>
              </div>

              <div class="card animal-table-card">
                <div class="card-header">
                  <h3>Historique hebdomadaire</h3>
                  <span class="muted">Poids et mortalité par semaine</span>
                </div>
                <table class="animal-info-table">
                  <thead>
                    <tr>
                      <th>Semaine</th>
                      <th>Poids (kg)</th>
                        <th>Réf. poids (kg)</th>
                      <th>Morts</th>
                      <th>Restants</th>
                        <th>Mortalité (%)</th>
                      <th>Note</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="info in animalInfos" :key="info.id">
                      <td>S{{ info.semaine_production }}</td>
                      <td>{{ info.poids_moyen !== null && info.poids_moyen !== undefined ? info.poids_moyen : '--' }}</td>
                        <td>
                          <span v-if="weightRefDisplay(info.semaine_production)">{{ weightRefDisplay(info.semaine_production) }}</span>
                          <span v-else class="muted">--</span>
                        </td>
                      <td>{{ info.morts_semaine || 0 }}</td>
                      <td>{{ info.animaux_restants !== null && info.animaux_restants !== undefined ? info.animaux_restants : '--' }}</td>
                        <td>
                          <div>{{ formatNumber(calculateWeeklyMortalityRate(info)) }} %</div>
                          <div class="muted small">Réf {{ mortalityRefDisplay(info.semaine_production) }}</div>
                        </td>
                      <td>{{ info.note || '--' }}</td>
                      <td class="table-actions">
                        <button class="icon-btn" title="Modifier" @click="startEditAnimalInfo(info)">✏️</button>
                        <button class="icon-btn danger" title="Supprimer" @click="deleteAnimalInfo(info)">🗑️</button>
                      </td>
                    </tr>
                    <tr v-if="animalInfos.length === 0">
                        <td colspan="7" class="muted">Aucune donnée pour l'instant.</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div class="card animal-visuals-card">
                <div class="card-header space-between">
                  <h3>Visualisations</h3>
                  <div class="legend">
                    <span class="legend-dot filled"></span> Observé
                    <span class="legend-dot free"></span> Réf. basse/haute
                  </div>
                </div>
                <div class="visuals-grid">
                  <div class="chart-item full-width">
                    <AnimalWeightChart
                      :labels="weightChartLabels"
                      :actual="weightActualSeries"
                      :ref-low="weightRefLowSeries"
                      :ref-high="weightRefHighSeries"
                    />
                  </div>
                  <div class="chart-item full-width">
                    <AnimalMortalityChart
                      :labels="animalLineLabels"
                      :series="animalMortalitySeries"
                      :ref-low="animalRefLowSeries"
                      :ref-high="animalRefHighSeries"
                    />
                  </div>
                  <div class="chart-item">
                    <AnimalWeeklyPie
                      :survived="animalPieSurvivors"
                      :deaths="animalPieDeaths"
                      title="Survie estimée"
                    />
                  </div>
                  <div class="chart-item">
                    <h4>Performance de survie</h4>
                    <PerformanceGauge :score="survivalPerformance" />
                    <p class="muted small">Objectif: rester au-dessus de 90% de survie.</p>
                  </div>
                  <div class="chart-item mortality-ref-card">
                    <div class="mortality-ref-header">
                      <div>
                        <h4>Références mortalité</h4>
                        <p class="muted small">Plage cible hebdo (basse / haute) et votre observé.</p>
                      </div>
                      <span class="pill subtle">S1-S12</span>
                    </div>
                    <table class="weekly-consumption-table mortality-ref-table">
                      <thead>
                        <tr>
                          <th>Semaine</th>
                          <th>Réf. basse</th>
                          <th>Réf. haute</th>
                          <th>Observé</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="row in mortalityReferenceRows" :key="row.week">
                          <td>S{{ row.week }}</td>
                          <td>{{ row.low }}%</td>
                          <td>{{ row.high }}%</td>
                          <td :class="{ 'text-good': (row.actual ?? 0) <= row.high, 'text-bad': (row.actual ?? 0) > row.high }">
                            {{ row.actual !== null && row.actual !== undefined ? row.actual + '%' : '--' }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <div class="card animal-advice-card">
                <div class="card-header space-between">
                  <h3>Alertes & conseils</h3>
                  <span class="pill subtle">Basé sur la dernière saisie</span>
                </div>
                <div class="advice-list">
                  <div
                    v-for="(advice, idx) in animalAdvice"
                    :key="idx"
                    :class="['advice', advice.level]"
                  >
                    {{ advice.text }}
                  </div>
                  <div v-if="!animalAdvice.length" class="muted">Aucune alerte pour l'instant.</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section
          v-if="activeTab === 'sante' && santeSubTab === 'traitements'"
          class="tab-panel traitements-panel"
        >
          <!-- Sante subtab controls -->
        <div v-if="activeTab === 'sante'" class="sante-subtabs" style="margin-top: 16px; gap: 10px; margin-left: 20px;">
          <button  :class="['finance-subtab', { active: santeSubTab === 'animaux' }]" @click="santeSubTab = 'animaux'">Animaux</button>
          <button :class="['finance-subtab', { active: santeSubTab === 'traitements' }]" @click="santeSubTab = 'traitements'">Traitements</button>
        </div>
          <div class="treatments-grid">
            <div class="card treatment-suggestions">
              <div class="card-header space-between">
                <div>
                  <h2>Traitements recommandés</h2>
                  <p class="muted small">Choisir une pathologie ou un symptôme pour pré-filtrer.</p>
                </div>
                <div class="chip-group">
                  <span class="pill subtle">Âge saisi: {{ animalAgeWeeks }} sem.</span>
                  <span class="pill subtle">Animaux: {{ survivorsCount }}</span>
                </div>
              </div>
              <div class="filter-row">
                <label>
                  Pathologie / maladie
                  <select v-model="selectedDisease">
                    <option value="">Toutes</option>
                    <option v-for="d in treatmentDiseaseOptions" :key="d" :value="d">{{ d }}</option>
                  </select>
                </label>
                <label>
                  Symptomatique
                  <select v-model="selectedSymptom">
                    <option value="">Tous</option>
                    <option v-for="s in treatmentSymptomOptions" :key="s" :value="s">{{ s }}</option>
                  </select>
                </label>
              </div>

              <div class="treatment-cards">
                <div
                  v-for="t in filteredTreatments"
                  :key="t.name"
                  class="treatment-card"
                >
                  <div class="medoc-thumb">
                    <img :src="getMedocImage(t.image)" @error="onMedocImgError" alt="photo traitement" />
                  </div>
                  <div class="medoc-body">
                    <div class="medoc-head">
                      <h4>{{ t.name }}</h4>
                      <span class="pill subtle">{{ t.type }}</span>
                    </div>
                    <p class="muted small">Couvre: {{ t.diseases.join(', ') }}</p>
                    <p class="medoc-desc">{{ t.description }}</p>
                    <p class="medoc-dose">Dose suggérée ({{ animalAgeWeeks }} sem.): {{ recommendedDose(t) }}</p>
                    <p class="medoc-note" v-if="t.caution">⚠️ {{ t.caution }}</p>
                    <div class="medoc-actions">
                      <button class="btn secondary" type="button" @click="prefillTreatment(t)">Pré-remplir</button>
                    </div>
                  </div>
                </div>
                <div v-if="!filteredTreatments.length" class="muted">Aucun traitement pour ce filtre.</div>
              </div>
            </div>

            <div class="card treatment-form-card">
              <div class="card-header space-between">
                <h3>Ajouter un traitement</h3>
                <span class="pill subtle">Non lié aux consommations</span>
              </div>
              <form class="treatment-form" @submit.prevent="addTreatmentRecord">
                <div class="form-row">
                  <label>
                    Pathologie
                    <input type="text" v-model="treatmentForm.maladie" placeholder="Ex: Salmonellose" />
                  </label>
                  <label>
                    Produit
                    <input type="text" v-model="treatmentForm.produit" placeholder="Ex: Baytril" />
                  </label>
                </div>
                <div class="form-row">
                  <label>
                    Dose / posologie
                    <input type="text" v-model="treatmentForm.dose" placeholder="Ex: 10 mg/kg/j 5 jours" />
                  </label>
                  <label>
                    Début
                    <input type="date" v-model="treatmentForm.debut" />
                  </label>
                  <label>
                    Fin
                    <input type="date" v-model="treatmentForm.fin" />
                  </label>
                </div>
                <div class="form-row">
                  <label>
                    Coût (FCFA)
                    <input type="number" min="0" step="1" v-model.number="treatmentForm.cout" />
                  </label>
                </div>
                <label>
                  Note / observation
                  <textarea rows="2" v-model="treatmentForm.note" placeholder="Observation, voie d'administration, retrait, etc."></textarea>
                </label>
                <div class="animal-info-actions">
                  <button class="btn" type="submit">Enregistrer</button>
                  <button class="btn secondary" type="button" @click="resetTreatmentForm">Vider</button>
                </div>
              </form>
            </div>

            <div class="card treatment-table-card">
              <div class="card-header space-between">
                <h3>Historique des traitements</h3>
                <span class="muted small">Liste locale</span>
              </div>
              <table class="treatment-table">
                <thead>
                  <tr>
                    <th>Pathologie</th>
                    <th>Produit</th>
                    <th>Posologie</th>
                    <th>Début</th>
                    <th>Fin</th>
                    <th>Note</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in treatmentRecords" :key="idx">
                    <td>{{ row.maladie || '—' }}</td>
                    <td>{{ row.produit || '—' }}</td>
                    <td>{{ row.dose || '—' }}</td>
                    <td>{{ row.debut || '—' }}</td>
                    <td>{{ row.fin || '—' }}</td>
                    <td>{{ row.note || '—' }}</td>
                  </tr>
                  <tr v-if="!treatmentRecords.length">
                    <td colspan="6" class="muted">Aucun traitement enregistré.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <section
          v-if="activeTab === 'finances'"
          class="tab-panel depenses-panel"
        >
          <h2>Finances</h2>
          <div class="finance-subtabs">
            <button
              :class="['finance-subtab', { active: financeSubTab === 'depenses' }]"
              @click="financeSubTab = 'depenses'"
            >
              Dépenses
            </button>
            <button
              :class="['subtab', { active: financeSubTab === 'gains' }]"
              @click="financeSubTab = 'gains'"
            >
              Gains
            </button>
          </div>

          <div v-if="financeSubTab === 'depenses'" class="finance-grid">
            <div class="card finance-block">
              <div class="card-header space-between">
                <div>
                  <h3>Dépenses élémentaires</h3>
                  <p class="muted small">Sélectionner un poste pour ajouter une dépense</p>
                </div>
                <span class="pill subtle">{{ expenseRecords.length }} enregs.</span>
              </div>
              <div class="expense-cards">
                <div
                  v-for="exp in expenseCatalog"
                  :key="exp.name"
                  class="expense-card"
                  @click="openExpenseDrawer(exp)"
                >
                  <div class="expense-thumb">
                    <img :src="getExpenseImage(exp.image)" @error="onMedocImgError" alt="dépense" />
                  </div>
                  <div class="expense-body">
                    <h4>{{ exp.name }}</h4>
                    <p class="muted small">{{ exp.description }}</p>
                  </div>
                </div>
              </div>
              <div class="muted small" style="margin-top: 10px;">
                Note : ajoutez aussi vos frais "Autres" et "Maintenance (autres)" pour capturer les dépenses imprévues et la maintenance générale.
              </div>
            </div>
          </div>

          <div v-if="financeSubTab === 'gains'" class="finance-grid gains-grid">
            <div class="card finance-block">
              <div class="card-header space-between gains-header">
                <div>
                  <h3>Gains</h3>
                  <p class="muted small">Suivi des gains observés vs référence (poids/semaine)</p>
                </div>
                <label class="price-input">
                  <span>Prix marché (FCFA / kg)</span>
                  <input type="number" min="0" step="10" v-model.number="gainPricePerKg" />
                </label>
              </div>

              <div class="gains-summary">
                <div class="gain-card">
                  <div class="label">Cumul observé</div>
                  <div class="value">{{ formatCurrencyFCFA(gainsComputed.cumActual, 0) }}</div>
                  <div class="hint">Basé sur poids saisis et mortalité</div>
                </div>
                <div class="gain-card">
                  <div class="label">Cumul référence</div>
                  <div class="value">{{ formatCurrencyFCFA(gainsComputed.cumRef, 0) }}</div>
                  <div class="hint">Poids de référence par semaine</div>
                </div>
                <div class="gain-card delta" :class="{ positive: gainsComputed.delta >= 0, negative: gainsComputed.delta < 0 }">
                  <div class="label">Écart</div>
                  <div class="value">{{ formatCurrencyFCFA(gainsComputed.delta, 0) }}</div>
                  <div class="hint">Observé - Référence</div>
                </div>
              </div>

              <div class="gains-performance">
                <PerformanceGauge :score="gainPerformanceScore" />
                <div class="perf-text">
                  <div class="label">Performance gains</div>
                  <div class="value">{{ gainPerformanceScore.toFixed(0) }}%</div>
                  <div class="hint">Ratio cumul observé / référence</div>
                </div>
              </div>

              <div class="profit-breakdown">
                <div class="profit-card revenue">
                  <div class="label">Gains observés</div>
                  <div class="value">{{ formatCurrencyFCFA(profitComputed.revenue, 0) }}</div>
                  <div class="hint">Cumuls (prix x poids saisis)</div>
                </div>
                <div class="profit-card reference">
                  <div class="label">Gains de référence</div>
                  <div class="value">{{ formatCurrencyFCFA(profitComputed.revenueRef, 0) }}</div>
                  <div class="hint">Poids de référence</div>
                </div>
                <div class="profit-card cost">
                  <div class="label">Consommations</div>
                  <div class="value">{{ formatCurrencyFCFA(totalCost, 0) }}</div>
                  <div class="hint">Coûts alimentation & eau</div>
                </div>
                <div class="profit-card cost">
                  <div class="label">Dépenses élémentaires</div>
                  <div class="value">{{ formatCurrencyFCFA(totalExpensesElementaires, 0) }}</div>
                  <div class="hint">Tiroir dépenses</div>
                </div>
                <div class="profit-card cost">
                  <div class="label">Traitements</div>
                  <div class="value">{{ formatCurrencyFCFA(totalTreatmentCost, 0) }}</div>
                  <div class="hint">Coûts saisis traitements</div>
                </div>
                <div class="profit-card total" :class="{ positive: profitComputed.profit >= 0, negative: profitComputed.profit < 0 }">
                  <div class="label">Bénéfice observé</div>
                  <div class="value">{{ formatCurrencyFCFA(profitComputed.profit, 0) }}</div>
                  <div class="hint">Gains observés - total coûts</div>
                </div>
              </div>

              <div class="gains-charts">
                <GainsLineChart
                  :labels="gainsComputed.labels"
                  :actual="gainsComputed.actual"
                  :reference="gainsComputed.reference"
                  :height="280"
                />
              </div>

              <div class="gains-footer">
                <div class="muted small">Ces estimations utilisent le prix marché saisi et vos données poids/mortalité hebdomadaires.</div>
                <button class="btn" type="button" @click="selectTab('predictions')">Passer aux prédictions</button>
              </div>
            </div>
          </div>

          <div class="expense-drawer" v-if="expenseDrawerOpen">
            <div class="expense-drawer-panel">
              <div class="expense-drawer-header">
                <div>
                  <h3>Ajouter une dépense</h3>
                  <p class="muted small">{{ expenseSelected?.name }}</p>
                </div>
                <button class="icon-btn" @click="closeExpenseDrawer">✕</button>
              </div>
              <form class="expense-form" @submit.prevent="saveExpense">
                <label>
                  Tâche / poste
                  <input type="text" v-model="expenseForm.tache" />
                </label>
                <div class="form-row">
                  <label>
                    Date
                    <input type="date" v-model="expenseForm.date" />
                  </label>
                  <label>
                    Montant (FCFA)
                    <input type="number" min="0" step="1" v-model.number="expenseForm.montant" />
                  </label>
                </div>
                <label>
                  Description
                  <textarea rows="2" v-model="expenseForm.description" placeholder="Détail de la dépense"></textarea>
                </label>
                <div class="animal-info-actions">
                  <button class="btn" type="submit">Enregistrer</button>
                  <button class="btn secondary" type="button" @click="closeExpenseDrawer">Annuler</button>
                </div>
              </form>
              <div class="expense-history">
                <h4>Historique local</h4>
                <ul>
                  <li v-for="(e, idx) in expenseRecords" :key="idx">
                    <strong>{{ e.tache || '—' }}</strong> — {{ e.date || '—' }} — {{ e.montant ? formatCurrencyFCFA(e.montant, 0) : 'Montant non saisi' }}
                    <div class="muted small">{{ e.description || '—' }}</div>
                  </li>
                  <li v-if="!expenseRecords.length" class="muted">Aucune dépense enregistrée.</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <div class="floating-messages" v-if="hasAnyMessages">
          <div class="floating-message-tabs">
            <button
              v-if="messageBuckets.critical.length"
              class="message-tab critical"
              :class="{ active: activeMessageTab === 'critical' }"
              @click="toggleMessageTab('critical')"
            >
              <span class="msg-icon">⚠️</span>
              Critiques
              <span class="badge" v-if="messageBuckets.critical.length">{{ messageBuckets.critical.length }}</span>
              <span class="tab-close" @click.stop="dismissMessageBucket('critical')">✕</span>
            </button>
            <button
              v-if="messageBuckets.problem.length"
              class="message-tab warning"
              :class="{ active: activeMessageTab === 'problem' }"
              @click="toggleMessageTab('problem')"
            >
              <span class="msg-icon">❗</span>
              Problèmes
              <span class="badge" v-if="messageBuckets.problem.length">{{ messageBuckets.problem.length }}</span>
              <span class="tab-close" @click.stop="dismissMessageBucket('problem')">✕</span>
            </button>
            <button
              v-if="messageBuckets.good.length"
              class="message-tab success"
              :class="{ active: activeMessageTab === 'good' }"
              @click="toggleMessageTab('good')"
            >
              <span class="msg-icon">✅</span>
              Bonnes nouvelles
              <span class="badge" v-if="messageBuckets.good.length">{{ messageBuckets.good.length }}</span>
              <span class="tab-close" @click.stop="dismissMessageBucket('good')">✕</span>
            </button>
          </div>

          <div class="floating-message-panel" v-if="messagesDrawerOpen">
            <div class="floating-message-header">
              <span>{{ activeMessageLabel }}</span>
              <button class="icon-btn" @click="messagesDrawerOpen = false">✕</button>
            </div>
            <ul class="floating-message-list">
              <li v-for="m in currentMessages" :key="m.id">
                <span class="msg-row">
                  <span class="msg-icon" aria-hidden="true">{{ messageIcon }}</span>
                  <span>{{ m.text }}</span>
                </span>
                <button class="link-btn" @click="dismissMessage(m.id)">OK</button>
              </li>
              <li v-if="!currentMessages.length" class="muted">Aucun message dans cette catégorie.</li>
            </ul>
          </div>
        </div>
      </main>
  </div>
</template>

<script>
import KPIDashboard from './Kpi.vue';
import ConsumptionHistoryChart from './charts/Consommation_chart.vue';
import ConsumptionCostChart from './charts/ConsumptionCostChart.vue';
import PredictionCharts from './charts/Prediction_chart.vue';
import AnimalMortalityChart from './charts/AnimalMortalityChart.vue';
import AnimalWeightChart from './charts/AnimalWeightChart.vue';
import AnimalWeeklyPie from './charts/AnimalWeeklyPie.vue';
import PerformanceGauge from './charts/PerformanceGauge.vue';
import GainsLineChart from './charts/GainsLineChart.vue';
import GainsBarChart from './charts/GainsBarChart.vue';
import WeightChart from './charts/WeightChart.vue';
import HydrationAreaChart from './charts/HydrationAreaChart.vue';
import CostBreakdownChart from './charts/CostBreakdownChart.vue';
import PopulationDonut from './charts/PopulationDonut.vue';
import WaterfallCostChart from './charts/WaterfallCostChart.vue';
import PerformanceChart from './charts/PerformanceChart.vue';
import FeedVolumeChart from './charts/FeedVolumeChart.vue';
import WaterVolumeChart from './charts/WaterVolumeChart.vue';
import TreatmentUsageChart from './charts/TreatmentUsageChart.vue';
import ExpenseDonutChart from './charts/ExpenseDonutChart.vue';
import KeyDatesTimeline from './charts/KeyDatesTimeline.vue';

// Methods modules
import * as dashboardMethods from './methods/dashboardMethods.js';
import * as consommationMethods from './methods/consommationMethods.js';
import * as predictionsMethods from './methods/predictionsMethods.js';
import * as animauxMethods from './methods/animauxMethods.js';
import * as chatbotMethods from './methods/chatbotMethods.js';
import * as financesMethods from './methods/financesMethods.js';
import * as tabUtils from './methods/tabUtils.js';
import * as messageMethods from './methods/messageMethods.js';
import * as traitementsMethods from './methods/traitementsMethods.js';
import * as depensesMethods from './methods/depensesMethods.js';
import * as gainsMethods from './methods/gainsMethods.js';

export default {
  name: 'Bandes',

  components: {
    KPIDashboard,
    ConsumptionHistoryChart,
    ConsumptionCostChart,
    PredictionCharts,
    AnimalMortalityChart,
    AnimalWeightChart,
    AnimalWeeklyPie,
    PerformanceGauge,
    GainsLineChart,
    GainsBarChart,
    WeightChart,
    HydrationAreaChart,
    CostBreakdownChart,
    PopulationDonut,
    WaterfallCostChart,
    PerformanceChart,
    FeedVolumeChart,
    WaterVolumeChart,
    TreatmentUsageChart,
    ExpenseDonutChart,
    KeyDatesTimeline
  },

  data() {
    return {
      id: null,
      band: null,
      activeTab: "dashboard",
      searchQuery: '',
      searchResults: [],
      searchFocusedIndex: 0,
      kpi: null,
      consommations: [],
      consumptionForm: { 
        date: new Date().toISOString().slice(0, 10),
        semaine_production: null,
        type: "",
        kg: 0,
        cout: 0,
        eau_litres: 0,
        prix_unitaire: 0,
        prix_eau_unitaire: 25
      },
      editingConsumptionId: null,
      consumptionFormCostPreview: 0,
      filledWeeks: new Map(),

      // server-side performance object for this band
      serverPerformance: null,

      animaux: [],
      animalInfos: [],
      animalInfoForm: {
        semaine_production: null,
        poids_moyen: null,
        morts_semaine: 0,
        animaux_restants: null,
        note: ''
      },
      editingAnimalInfoId: null,
      consumptionReference: [
        { week: 1, aliment_kg: 150, eau_litres: 300, prix_unitaire: 0.45 },
        { week: 2, aliment_kg: 420, eau_litres: 640, prix_unitaire: 0.45 },
        { week: 3, aliment_kg: 730, eau_litres: 980, prix_unitaire: 0.48 },
        { week: 4, aliment_kg: 1100, eau_litres: 1350, prix_unitaire: 0.5 },
        { week: 5, aliment_kg: 1450, eau_litres: 1680, prix_unitaire: 0.52 },
        { week: 6, aliment_kg: 1750, eau_litres: 1900, prix_unitaire: 0.55 },
        { week: 7, aliment_kg: 1950, eau_litres: 2050, prix_unitaire: 0.58 },
        { week: 8, aliment_kg: 2050, eau_litres: 2150, prix_unitaire: 0.6 }
      ],
      weightReference: [
        { week: 1, low: 0.08, high: 0.12 },
        { week: 2, low: 0.18, high: 0.25 },
        { week: 3, low: 0.30, high: 0.45 },
        { week: 4, low: 0.50, high: 0.70 },
        { week: 5, low: 0.70, high: 1.00 },
        { week: 6, low: 0.90, high: 1.30 },
        { week: 7, low: 1.05, high: 1.55 },
        { week: 8, low: 1.20, high: 1.80 },
        { week: 9, low: 1.35, high: 2.00 },
        { week: 10, low: 1.50, high: 2.20 },
        { week: 11, low: 1.50, high: 2.20 },
        { week: 12, low: 1.50, high: 2.20 }
      ],
      mortalityReference: [
        { week: 1, low: 0, high: 1.0 },
        { week: 2, low: 0, high: 0.8 },
        { week: 3, low: 0, high: 0.6 },
        { week: 4, low: 0, high: 0.5 },
        { week: 5, low: 0, high: 0.4 },
        { week: 6, low: 0, high: 0.4 },
        { week: 7, low: 0, high: 0.3 },
        { week: 8, low: 0, high: 0.3 },
        { week: 9, low: 0, high: 0.25 },
        { week: 10, low: 0, high: 0.25 },
        { week: 11, low: 0, high: 0.20 },
        { week: 12, low: 0, high: 0.20 }
      ],
      interventions: [],
      predictions: [],
      optimalPrediction: null,
      totalPredictedProfit: 0,
      _fetchingTab: null,
      messages: [
        { from: 'bot', text: 'Bonjour ! Comment puis-je vous aider avec votre bande avicole ?' }
      ],
      chatInput: "",
      chatMode: 'data',
      chatLoading: false,
      
      // Prediction data
      predictionDays: '7',
      predictionErrorMsg: '',
      
      // Trends dans un objet pour éviter les erreurs
      trends: {
        poids: 2.5,
        cout: -1.2,
        mortalite: 0.5,
        ic: -0.8
      },
      
      // Metrics
      totalPredictedProfit: 0,
      optimalSellingDate: '',
      roi: 0,
      
      // Alerts
      alerts: [
        { id: 1, level: 'medium', message: 'Consommation élevée cette semaine' },
        { id: 2, level: 'low', message: 'Poids dans la moyenne' },
        { id: 3, level: 'high', message: 'Taux de mortalité à surveiller' }
      ],
      alertsDrawerOpen: false,
      messagesDrawerOpen: false,
      activeMessageTab: 'critical',
      dismissedMessageIds: [],

      selectedDisease: '',
      selectedSymptom: '',
      santeSubTab: 'animaux',
      treatmentForm: {
        maladie: '',
        produit: '',
        dose: '',
        debut: new Date().toISOString().slice(0, 10),
        fin: '',
        note: '',
        cout: 0
      },
      treatmentRecords: [],
      medocPlaceholder: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"><rect width="80" height="80" fill="%23e5e7eb"/><text x="40" y="46" font-size="18" text-anchor="middle" fill="%236b7280">Rx</text></svg>',
      treatmentCatalog: [
        {
          name: 'Baytril',
          type: 'Antibiotique (enrofloxacine)',
          diseases: ['salmonellose', 'colibacillose', 'entérite'],
          symptoms: ['diarrhée', 'abattement', 'respiratoire'],
          description: 'Enrofloxacine, large spectre pour salmonellose / entérites / colibacillose.',
          doses: [
            { maxWeek: 2, text: '8-10 mg/kg/j (eau) pendant 3 jours' },
            { maxWeek: 5, text: '10-12 mg/kg/j (eau) pendant 3-5 jours' },
            { maxWeek: 99, text: '12-15 mg/kg/j (eau) pendant 5 jours' }
          ],
          caution: 'Ne pas associer macrolides, tétracyclines, théophylline.',
          image: '../assets/medoc_photo/Baytril.png',
          cost: 6500
        },
        {
          name: 'Lévomycétine',
          type: 'Antibiotique',
          diseases: ['entérite', 'respiratoire'],
          symptoms: ['diarrhée', 'toux'],
          description: 'Chloramphénicol, pathologies intestinales et respiratoires.',
          doses: [
            { maxWeek: 2, text: '3-5 mg/kg 2x/j 5 jours' },
            { maxWeek: 6, text: '5-10 mg/kg 2x/j 5-7 jours' },
            { maxWeek: 99, text: '15-20 mg/kg/j 5-7 jours' }
          ],
          caution: 'Ne pas dépasser 2 semaines de cure.',
          image: '../assets/medoc_photo/evomycetine.png',
          cost: 5200
        },
        {
          name: 'Dithrim',
          type: 'Antibiotique (TMP + sulfadimézine)',
          diseases: ['digestif', 'respiratoire'],
          symptoms: ['diarrhée', 'toux'],
          description: 'Association triméthoprime + sulfadimézine, large spectre.',
          doses: [
            { maxWeek: 2, text: '0.2 ml/kg/j (inj) 3 jours' },
            { maxWeek: 6, text: '0.3 ml/kg/j (inj) 3-5 jours' },
            { maxWeek: 99, text: '0.35 ml/kg/j (inj) 5 jours' }
          ],
          caution: 'Peut causer troubles digestifs et somnolence.',
          image: '../assets/medoc_photo/Dithrim.png',
          cost: 4800
        },
        {
          name: 'Enroflon',
          type: 'Antibiotique (enrofloxacine)',
          diseases: ['prévention respiratoire', 'digestif'],
          symptoms: ['prévention', 'respiratoire'],
          description: 'Solution en eau, prophylaxie et traitement respiratoire/digestif.',
          doses: [
            { maxWeek: 2, text: '0.5 ml/L eau 3 jours' },
            { maxWeek: 6, text: '1 ml/L eau 3-5 jours' },
            { maxWeek: 99, text: '1-1.5 ml/L eau 5 jours' }
          ],
          image: '../assets/medoc_photo/Enroflon.png',
          cost: 4300
        },
        {
          name: 'Doreen',
          type: 'Antibiotique (rifampicine + doxycycline)',
          diseases: ['salmonellose', 'gastro-entérite'],
          symptoms: ['diarrhée', 'fièvre'],
          description: 'Poudre à reconstituer, actif sur salmonelles et entérites.',
          doses: [
            { maxWeek: 2, text: '10 mg/kg/j 3 jours' },
            { maxWeek: 6, text: '15 mg/kg/j 5 jours' },
            { maxWeek: 99, text: '20 mg/kg/j 5-7 jours' }
          ],
          image: '../assets/medoc_photo/Doreen.png',
          cost: 5600
        },
        {
          name: 'Amoxicilline',
          type: 'Antibiotique',
          diseases: ['digestif', 'respiratoire', 'urinaire'],
          symptoms: ['toux', 'diarrhée'],
          description: 'Poudre large spectre pour voies digestives, respiratoires et urinaires.',
          doses: [
            { maxWeek: 2, text: '10-12 mg/kg/j 3 jours' },
            { maxWeek: 6, text: '15 mg/kg/j 5 jours' },
            { maxWeek: 99, text: '20 mg/kg/j 5-7 jours' }
          ],
          image: '../assets/medoc_photo/Amoxicilline.png',
          cost: 5100
        },
        {
          name: 'Doxycycline',
          type: 'Antibiotique (tétracycline)',
          diseases: ['respiratoire'],
          symptoms: ['toux', 'écoulement'],
          description: 'Poudre pour eau, infections respiratoires bactériennes.',
          doses: [
            { maxWeek: 2, text: '10 mg/kg/j 3 jours' },
            { maxWeek: 6, text: '15 mg/kg/j 5 jours' },
            { maxWeek: 99, text: '20 mg/kg/j 5-7 jours' }
          ],
          image: '../assets/medoc_photo/Doxycycline.png',
          cost: 4700
        },
        {
          name: 'Trichopole (métronidazole)',
          type: 'Antiprotozoaire',
          diseases: ['coccidiose', 'protozoaires'],
          symptoms: ['diarrhée', 'selles sanglantes'],
          description: 'Métronidazole contre coccidies et protozoaires intestinaux.',
          doses: [
            { maxWeek: 2, text: '10 mg/kg/j 3 jours' },
            { maxWeek: 6, text: '15 mg/kg/j 5 jours' },
            { maxWeek: 99, text: '20 mg/kg/j 5-7 jours' }
          ],
          image: '../assets/medoc_photo/Trichopole.png',
          cost: 3900
        },
        {
          name: 'Furazolidone',
          type: 'Antibiotique (nitrofurane)',
          diseases: ['digestif', 'colibacillose'],
          symptoms: ['diarrhée'],
          description: 'Nitrofurane, crée un milieu défavorable aux bactéries intestinales.',
          doses: [
            { maxWeek: 2, text: '5 mg/kg/j 5 jours' },
            { maxWeek: 6, text: '7 mg/kg/j 5 jours' },
            { maxWeek: 99, text: '10 mg/kg/j 5-7 jours' }
          ],
          image: '../assets/medoc_photo/Furazolidone.png',
          cost: 3600
        },
        {
          name: 'Tétracycline',
          type: 'Antibiotique',
          diseases: ['respiratoire', 'digestif'],
          symptoms: ['toux', 'diarrhée'],
          description: 'Large spectre, améliore aussi l’état digestif si bien dosé.',
          doses: [
            { maxWeek: 2, text: '10 mg/kg/j 3 jours' },
            { maxWeek: 6, text: '15 mg/kg/j 5 jours' },
            { maxWeek: 99, text: '20 mg/kg/j 5-7 jours' }
          ],
          image: '../assets/medoc_photo/Tétracycline.png',
          cost: 4500
        },
        {
          name: 'Biomycine',
          type: 'Antibiotique',
          diseases: ['croissance', 'prévention'],
          symptoms: ['retard de croissance'],
          description: 'Poudre stimulante de croissance, augmente le gain pondéral.',
          doses: [
            { maxWeek: 2, text: '10 mg/kg/j 3 jours' },
            { maxWeek: 6, text: '12 mg/kg/j 5 jours' },
            { maxWeek: 99, text: '15 mg/kg/j 5-7 jours' }
          ],
          image: '../assets/medoc_photo/Biomycine.png',
          cost: 4200
        },
        {
          name: 'Sulfadimezin',
          type: 'Sulfamidé',
          diseases: ['coccidiose', 'respiratoire', 'typhoïde'],
          symptoms: ['diarrhée', 'respiratoire'],
          description: 'Sulfamide moins toxique, utile sur coccidiose et affections respiratoires.',
          doses: [
            { maxWeek: 2, text: '20 mg/kg/j 3 jours' },
            { maxWeek: 6, text: '25 mg/kg/j 3-5 jours' },
            { maxWeek: 99, text: '30 mg/kg/j 5 jours' }
          ],
          image: '../assets/medoc_photo/Sulfadimezine.png',
          cost: 3300
        },
        {
          name: 'Chlortétracycline',
          type: 'Tétracycline',
          diseases: ['coccidiose', 'pneumonie', 'mycoplasmose'],
          symptoms: ['toux', 'respiratoire'],
          description: 'Poudre jaune, prévention et traitement coccidiose/pneumonie.',
          doses: [
            { maxWeek: 2, text: '10 mg/kg/j 3 jours' },
            { maxWeek: 6, text: '15 mg/kg/j 5 jours' },
            { maxWeek: 99, text: '20 mg/kg/j 5-7 jours' }
          ],
          image: '../assets/medoc_photo/Chlortétracycline.png',
          cost: 4000
        }
      ],

      financeSubTab: 'depenses',

      expenseCatalog: [
        { name: 'Chauffage', image: '../assets/depense_photo/chauffage.png', description: 'Gaz, fioul ou électrique pour maintenir la température.' },
        { name: 'Électricité', image: '../assets/depense_photo/electricite.png', description: 'Éclairage, ventilation, automatisation.' },
        { name: 'Transport', image: '../assets/depense_photo/transport.png', description: 'Acheminement aliments, animaux ou produits.' },
        { name: 'Copeaux / litière', image: '../assets/depense_photo/copeau.png', description: 'Approvisionnement en litière pour confort et hygiène.' },
        { name: 'Nettoyage / désinfection', image: '../assets/depense_photo/nettoyage.png', description: 'Produits et prestations de biosécurité.' },
        { name: 'Taxes / redevances', image: '../assets/depense_photo/taxes.png', description: 'Taxes locales et redevances administratives.' },
        { name: 'Installation / maintenance', image: '../assets/depense_photo/installation.png', description: 'Réparations, maintenance d’équipements.' },
        { name: 'Maintenance (autres)', image: '../assets/depense_photo/maintenance.png', description: 'Maintenance générale hors installations principales.' },
        { name: 'Autres', image: '../assets/depense_photo/autres.png', description: 'Dépenses diverses et imprévues.' }
      ],
      gainPricePerKg: 1200,
      expenseDrawerOpen: false,
      expenseSelected: null,
      expenseForm: {
        tache: '',
        date: new Date().toISOString().slice(0, 10),
        description: '',
        montant: null
      },
      expenseRecords: []
      ,selectedHelpSubTab: 'dashboard'
      ,helpSections: [
        {
          key: 'dashboard',
          label: 'Dashboard',
          cards: [
            {
              badge: 'Vue globale',
              title: 'Lire les KPIs instantanés',
              summary: 'Suivez poids, coût total, mortalité et IC en un coup d’œil.',
              steps: ['Vérifiez les cartes en haut', 'Survolez les courbes pour voir les valeurs', 'Ouvrez les alertes si un indicateur est rouge'],
              image: null,
              targetTab: 'dashboard'
            },
            {
              badge: 'Chrono',
              title: 'Chronologie des consommations',
              summary: 'Liste et graphiques des apports récents.',
              steps: ['Descendez jusqu’aux listes', 'Filtrez par semaine si besoin', 'Ajoutez une conso depuis l’onglet Consommation'],
              image: null,
              targetTab: 'consommation'
            }
          ]
        },
        {
          key: 'consommation',
          label: 'Consommation',
          cards: [
            {
              badge: 'Saisie',
              title: 'Ajouter une consommation',
              summary: 'Renseignez semaine, type, kg, coût et eau.',
              steps: ['Choisissez la semaine de production', 'Saisissez kg et coût (auto si prix/kg)', 'Validez pour mettre à jour les tendances'],
              image: null,
              targetTab: 'consommation'
            },
            {
              badge: 'Qualité données',
              title: 'Compléter les semaines manquantes',
              summary: 'Les semaines sautées peuvent être auto-remplies à 0 pour garder la courbe propre.',
              steps: ['Si une semaine est vide, ajoutez une entrée 0', 'Les prédictions utiliseront ces zéros pour éviter des trous'],
              image: null,
              targetTab: 'consommation'
            }
          ]
        },
        {
          key: 'predictions',
          label: 'Prédictions',
          cards: [
            {
              badge: 'Projection',
              title: 'Lire les marges futures',
              summary: 'Marge et poids projetés selon l’horizon choisi.',
              steps: ['Choisissez la durée (jours)', 'Comparez marge et survie projetées', 'Ajustez les coûts si besoin dans Consommation'],
              image: null,
              targetTab: 'predictions'
            }
          ]
        },
        {
          key: 'kpi',
          label: 'KPIs',
          cards: [
            {
              badge: 'Performance',
              title: 'Comparer les axes clés',
              summary: 'Suivez coûts, conso et IC sur plusieurs axes.',
              steps: ['Survolez les courbes multi-axes', 'Regardez le donut top dépenses', 'Ouvrez les détails financiers pour les coûts/kg'],
              image: null,
              targetTab: 'kpi'
            }
          ]
        },
        {
          key: 'sante',
          label: 'Santé',
          cards: [
            {
              badge: 'Animaux',
              title: 'Saisir poids et mortalité',
              summary: 'Chaque semaine, ajoutez poids, morts et restants.',
              steps: ['Choisissez la semaine', 'Ajoutez poids, morts, restants', 'Suivez la courbe poids et mortalité vs référentiels'],
              image: null,
              targetTab: 'animaux'
            },
            {
              badge: 'Traitements',
              title: 'Gérer les traitements',
              summary: 'Filtres par pathologie/symptôme, pré-remplissage et suivi des coûts.',
              steps: ['Filtrez par maladie ou symptôme', 'Pré-remplissez puis ajustez dose', 'Enregistrez pour suivre le coût total'],
              image: null,
              targetTab: 'traitements'
            }
          ]
        },
        {
          key: 'finances',
          label: 'Finances',
          cards: [
            {
              badge: 'Dépenses',
              title: 'Suivre dépenses et traitements',
              summary: 'Enregistrez dépenses élémentaires et charges santé pour les coûts totaux.',
              steps: ['Ajoutez une dépense avec montant et image', 'Ajoutez les traitements (coûts)', 'Vérifiez la marge dans KPI'],
              image: null,
              targetTab: 'finances'
            }
          ]
        },
        {
          key: 'infos',
          label: 'Infos',
          cards: [
            {
              badge: 'Fiche',
              title: 'Comprendre la fiche bande',
              summary: 'Résumé identités, chronologie, sanitaire et finance express.',
              steps: ['Lisez les cartes Statut & Chronologie', 'Contrôlez mortalité et traitements', 'Suivez coûts et ROI rapide'],
              image: null,
              targetTab: 'infos'
            }
          ]
        }
      ]
    };
  },
  
  computed: {
    currentHelpCards() {
      const section = this.helpSections.find(s => s.key === this.selectedHelpSubTab) || this.helpSections[0];
      return section ? section.cards : [];
    },

    durationWeeks() {
      return Math.max(1, Math.ceil((this.band?.duree_jours || 42) / 7));
    },

    currentAnimals() {
      if (!this.band) return 0;
      const base = this.band.nombre_initial || 0;
      const deaths = this.animalInfos.length ? this.totalAnimalDeaths : (this.band.nombre_morts_totaux || 0);
      return Math.max(0, base - deaths);
    },

    totalAnimalDeaths() {
      return this.animalInfos.reduce((sum, info) => sum + (info.morts_semaine || 0), 0);
    },

    survivorsCount() {
      const initial = this.band?.nombre_initial || 0;
      return Math.max(0, initial - this.totalAnimalDeaths);
    },

    gainsComputed() { return gainsMethods.computeGainsComputed(this); },

    gainPerformanceScore() { return gainsMethods.computeGainPerformanceScore(this); },

    totalExpensesElementaires() {
      return (this.expenseRecords || []).reduce((sum, e) => sum + (Number(e?.montant) || 0), 0);
    },

    totalTreatmentCost() {
      return (this.treatmentRecords || []).reduce((sum, t) => sum + (Number(t?.cout) || 0), 0);
    },

    treatmentProductCount() {
      const unique = new Set();
      (this.treatmentRecords || []).forEach(t => {
        if (t?.produit) unique.add(t.produit);
      });
      return unique.size;
    },

    totalTreatmentDays() {
      const dayMs = 1000 * 60 * 60 * 24;
      return (this.treatmentRecords || []).reduce((sum, t) => {
        if (!t?.debut || !t?.fin) return sum;
        const start = new Date(t.debut);
        const end = new Date(t.fin);
        if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return sum;
        const diff = Math.max(0, Math.round((end - start) / dayMs));
        return sum + (diff + 1);
      }, 0);
    },

    totalCostsAll() {
      return this.totalCost + this.totalExpensesElementaires + this.totalTreatmentCost;
    },

    profitComputed() { return gainsMethods.computeProfitComputed(this); },

    weekOptions() {
      const usedWeeks = new Set(
        this.consommations
          .filter(c => c.id !== this.editingConsumptionId)
          .map(c => c.semaine_production)
      );
      // Autocomplete des semaines précédentes manquantes à 0 si une semaine future est saisie
      return Array.from({ length: this.durationWeeks }, (_, idx) => {
        const week = idx + 1;
        return { week, disabled: usedWeeks.has(week) };
      });
    },

    nextAvailableWeek() {
      const available = this.weekOptions.find(w => !w.disabled);
      return available ? available.week : (this.weekOptions.length ? this.weekOptions.length + 1 : 1);
    },

    animalWeekOptions() {
      return Array.from({ length: this.durationWeeks }, (_, idx) => {
        const week = idx + 1;
        const hasInfo = this.animalInfos.some(info => info.semaine_production === week);
        return { week, hasInfo };
      });
    },

    nextAnimalWeek() {
      const used = new Set(this.animalInfos.map(i => i.semaine_production));
      for (let w = 1; w <= this.durationWeeks; w += 1) {
        if (!used.has(w)) return w;
      }
      return Math.min(this.durationWeeks + 1, this.durationWeeks);
    },

    animalAgeWeeks() {
      return this.lastAnimalWeek || 0;
    },

    lastAnimalWeek() {
      if (!this.animalInfos.length) return null;
      return [...this.animalInfos]
        .filter(i => i.semaine_production)
        .sort((a, b) => b.semaine_production - a.semaine_production)[0].semaine_production;
    },

    animalLastWeight() {
      const withWeight = this.animalInfos
        .filter(i => i.poids_moyen !== null && i.poids_moyen !== undefined)
        .sort((a, b) => (b.semaine_production || 0) - (a.semaine_production || 0));
      if (!withWeight.length) return null;
      return { value: withWeight[0].poids_moyen, week: withWeight[0].semaine_production };
    },

    survivalPerformance() {
      const initial = this.band?.nombre_initial || 0;
      if (!initial) return 0;
      return Math.round((this.survivorsCount / initial) * 100);
    },

    currentProductionWeek() {
      if (!this.band?.date_arrivee) return 0;
      const start = new Date(this.band.date_arrivee);
      const now = new Date();
      const diffDays = Math.floor((now.setHours(0, 0, 0, 0) - start.setHours(0, 0, 0, 0)) / (1000 * 60 * 60 * 24));
      const week = Math.floor(diffDays / 7) + 1;
      return Math.min(Math.max(week, 1), this.durationWeeks);
    },

    ageLabel() {
      if (!this.band?.date_arrivee) return '—';
      const start = new Date(this.band.date_arrivee);
      const now = new Date();
      const diffDays = Math.max(0, Math.floor((now - start) / (1000 * 60 * 60 * 24)));
      if (diffDays < 14) return `${diffDays} jours`;
      const weeks = Math.floor(diffDays / 7);
      return `${weeks} semaines`;
    },

    animalLineLabels() {
      return this.animalInfos.map(info => `S${info.semaine_production}`);
    },

    animalMortalitySeries() {
      const initial = this.band?.nombre_initial || 0;
      if (!initial) return this.animalInfos.map(() => 0);
      return this.animalInfos.map(info => this.calculateWeeklyMortalityRate(info));
    },

    animalRefLowSeries() {
      return this.animalInfos.map(info => this.getMortalityRef(info.semaine_production).low);
    },

    animalRefHighSeries() {
      return this.animalInfos.map(info => this.getMortalityRef(info.semaine_production).high);
    },

    weightReferenceFiltered() {
      const maxWeek = Math.min(
        this.durationWeeks,
        Math.max(...this.weightReference.map(r => r.week))
      );
      return this.weightReference.filter(r => r.week <= maxWeek);
    },

    weightChartLabels() {
      return this.weightReferenceFiltered.map(r => `S${r.week}`);
    },

    weightActualSeries() {
      return this.weightReferenceFiltered.map(ref => {
        const info = this.animalInfos.find(i => i.semaine_production === ref.week);
        return info && info.poids_moyen !== null && info.poids_moyen !== undefined
          ? Number(info.poids_moyen)
          : null;
      });
    },

    weightRefLowSeries() {
      return this.weightReferenceFiltered.map(r => r.low);
    },

    weightRefHighSeries() {
      return this.weightReferenceFiltered.map(r => r.high);
    },

    animalPieSurvivors() {
      return this.survivorsCount;
    },

    animalPieDeaths() {
      return this.totalAnimalDeaths;
    },

    mortalityReferenceRows() {
      return this.mortalityReference.map(ref => {
        const actual = this.animalInfos.find(info => info.semaine_production === ref.week);
        return {
          ...ref,
          actual: actual ? this.calculateWeeklyMortalityRate(actual) : null
        };
      });
    },

    animalAdvice() {
      if (!this.animalInfos.length) return [];
      const last = [...this.animalInfos]
        .filter(i => i.semaine_production)
        .sort((a, b) => b.semaine_production - a.semaine_production)[0];
      const adv = [];
      const ref = this.getMortalityRef(last.semaine_production);
      const actualRate = this.calculateWeeklyMortalityRate(last);

      if (actualRate > ref.high) {
        adv.push({ level: 'warning', text: `S${last.semaine_production}: mortalité ${actualRate}% au-dessus du seuil (${ref.high}%). Vérifier ventilation, eau et densité.` });
      } else {
        adv.push({ level: 'info', text: `S${last.semaine_production}: mortalité ${actualRate}% dans les bornes (${ref.low}-${ref.high}%). Continuer la surveillance.` });
      }

      if (last.poids_moyen !== null && last.poids_moyen !== undefined && last.poids_moyen < 1 && last.semaine_production >= 3) {
        adv.push({ level: 'warning', text: `S${last.semaine_production}: poids moyen ${last.poids_moyen} kg. Vérifier apport protéique et appétence.` });
      }

      if (this.survivalPerformance < 85) {
        adv.push({ level: 'warning', text: `Survie à ${this.survivalPerformance}%. Prioriser hygiène, eau fraîche et contrôle pathologies.` });
      }

      return adv;
    },

    treatmentDiseaseOptions() {
      const set = new Set();
      this.treatmentCatalog.forEach(t => t.diseases.forEach(d => set.add(d)));
      return Array.from(set);
    },

    treatmentSymptomOptions() {
      const set = new Set();
      this.treatmentCatalog.forEach(t => (t.symptoms || []).forEach(s => set.add(s)));
      return Array.from(set);
    },

    filteredTreatments() {
      return this.treatmentCatalog.filter(t => {
        const matchesDisease = this.selectedDisease ? t.diseases.includes(this.selectedDisease) : true;
        const matchesSymptom = this.selectedSymptom ? (t.symptoms || []).includes(this.selectedSymptom) : true;
        return matchesDisease && matchesSymptom;
      });
    },

    weeklyConsumptionRows() {
      if (!this.band) return [];

      const startDate = this.band?.date_arrivee ? new Date(this.band.date_arrivee) : null;
      return Array.from({ length: this.durationWeeks }, (_, idx) => {
        const week = idx + 1;
        const cons = this.consommations.find(c => c.semaine_production === week) || null;
        const prixUnitaire = cons
          ? (cons.prix_unitaire || (cons.kg ? (cons.cout || 0) / cons.kg : 0))
          : null;
        const prixEau = cons ? (cons.prix_eau_unitaire ?? 25) : null;
        const cost = cons ? (cons.cout || 0) : 0;

        return {
          week,
          aliment: cons ? `${this.formatNumber(cons.kg)} kg` : '—',
          eau: cons ? `${this.formatNumber(cons.eau_litres)} L` : '—',
          prixUnitaire: prixUnitaire ? `${this.formatNumber(prixUnitaire, 0)} FCFA/kg` : '—',
          prixEau: prixEau !== null ? `${this.formatNumber(prixEau, 0)} FCFA/L` : '—',
          cout: cons ? this.formatCurrencyFCFA(cost, 0) : '—',
          consumptionId: cons?.id || null
        };
      });
    },

    mortalityRate() {
      if (!this.band || !this.band.nombre_initial || this.band.nombre_initial === 0) return 0;
      const morts = this.band.nombre_morts_totaux || 0;
      return ((morts / this.band.nombre_initial) * 100).toFixed(1);
    },
    
    totalCost() {
      return this.consommations.reduce((total, c) => total + (c.cout || 0), 0);
    },

    feedPerBird() {
      const animals = Number(this.band?.nombre_initial || 0);
      if (!animals) return '0.00';
      const total = this.consommations.reduce((sum, c) => sum + (Number(c.kg) || 0), 0);
      return (total / animals).toFixed(2);
    },

    waterPerBird() {
      const animals = Number(this.band?.nombre_initial || 0);
      if (!animals) return '0.00';
      const total = this.consommations.reduce((sum, c) => sum + (Number(c.eau_litres) || 0), 0);
      return (total / animals).toFixed(2);
    },
    
    consumptionIndex() {
      if (this.currentAnimals === 0 || this.totalCost === 0) return 0;
      return (this.totalCost / this.currentAnimals).toFixed(2);
    },
    
    averageDailyCost() {
      if (this.consommations.length === 0) return 0;
      const days = Math.max(1, this.consommations.length);
      return +(this.totalCost / days).toFixed(0);
    },
    
    productivityScore() {
      // Combine survival and weight attainment into a stable 0-100 score
      const survival = Number(this.survivalPerformance || 0);
      const actualWeight = this.animalLastWeight?.value || null;
      const weightWeek = this.animalLastWeight?.week || this.currentProductionWeek || null;
      const refObj = (this.weightReference || []).find(r => r.week === weightWeek);
      const refWeight = refObj ? ((refObj.low + refObj.high) / 2) : null;
      const weightScore = (refWeight && actualWeight) ? this.ratioScore(refWeight, actualWeight) : 50; // default neutral
      return Math.round((survival + weightScore) / 2);
    },

    // Global consolidated performance for the current bande (0-100)
    performancePercent() {
      // Prefer localStorage precomputed map first
      try {
        const raw = localStorage.getItem('band_performance_map');
        if (raw) {
          const map = JSON.parse(raw);
          if (map && typeof map === 'object') {
            const val = map[this.id];
            if (typeof val === 'number') return val;
            // allow legacy components_xxx
            const compKey = `components_${this.id}`;
            if (map[compKey] && typeof map[compKey] === 'object' && typeof map[compKey].cost === 'number') {
              // compute average of subscores if present
              const subs = Object.values(map[compKey]).filter(v => typeof v === 'number');
              if (subs.length) return Math.round(subs.reduce((a, b) => a + b, 0) / subs.length);
            }
          }
        }
      } catch (e) { /* ignore parse errors */ }

      // Prefer server-side computed performance if available
      if (this.serverPerformance && typeof this.serverPerformance.performance_percent === 'number') {
        return this.serverPerformance.performance_percent;
      }

      // No client-side global performance calculation — rely on backend/localStorage map
      try {
        const raw = localStorage.getItem('band_performance_map');
        if (raw) {
          const map = JSON.parse(raw);
          if (map && typeof map === 'object') {
            const val = map[this.id];
            if (typeof val === 'number') return val;
            const compKey = `components_${this.id}`;
            if (map[compKey] && typeof map[compKey] === 'object') {
              const subs = Object.values(map[compKey]).filter(v => typeof v === 'number');
              if (subs.length) return Math.round(subs.reduce((a, b) => a + b, 0) / subs.length);
            }
          }
        }
      } catch (e) { /* ignore parse errors */ }

      if (this.serverPerformance && typeof this.serverPerformance.performance_percent === 'number') {
        return this.serverPerformance.performance_percent;
      }

      // Unknown: return 0 (explicit) rather than computing locally to avoid divergence
      return 0;
    },

    recentConsumptions() {
      return this.consommations
        .slice()
        .sort((a, b) => new Date(b.date || b.created_at || 0) - new Date(a.date || a.created_at || 0))
        .slice(0, 5);
    },

    dashboardInsights() {
      const insights = [];
      const initial = this.band?.nombre_initial || 0;
      const alive = this.survivorsCount;
      const survival = initial ? Math.round((alive / initial) * 100) : 0;
      const lastCons = this.consommations
        .slice()
        .sort((a, b) => new Date(b.date || b.created_at || 0) - new Date(a.date || a.created_at || 0))[0];

      insights.push({
        title: 'Capacité & survie',
        value: `${alive}/${initial}`,
        detail: survival ? `Survie ${survival}% — ${this.mortalityRate}% de mortalité cumulée.` : 'Survie à calculer (ajoutez les effectifs).',
        tone: survival < 85 ? 'warning' : 'success'
      });

      insights.push({
        title: 'Coûts engagés',
        value: this.formatCurrencyFCFA(this.totalCostsAll, 0),
        detail: `IC actuel ${this.consumptionIndex || 0} FCFA/poule. Coût moyen jour ${this.formatCurrencyFCFA(this.averageDailyCost, 0)}.`,
        tone: this.totalCostsAll > 0 ? 'info' : 'neutral'
      });

      insights.push({
        title: 'Dernière consommation',
        value: lastCons ? `${this.formatNumber(lastCons.kg || 0)} kg` : '—',
        detail: lastCons ? `${this.formatDate(lastCons.date)} • ${lastCons.type || 'Aliment'} • ${this.formatCurrencyFCFA(lastCons.cout || 0)}` : 'Ajoutez une première consommation pour tracer la courbe.',
        tone: lastCons ? 'info' : 'neutral'
      });

      return insights;
    },

    consumptionPeriod() {
      if (!this.band?.date_arrivee) return { start: null, end: null };
      const startDate = new Date(this.band.date_arrivee);
      const durationDays = parseInt(this.band?.duree_jours, 10) || 42;
      const endDate = new Date(startDate);
      endDate.setDate(startDate.getDate() + durationDays - 1);
      return {
        start: startDate.toLocaleDateString('fr-FR'),
        end: endDate.toLocaleDateString('fr-FR')
      };
    },

    bandDateRange() {
      const startStr = this.band?.date_arrivee;
      if (!startStr) return { start: null, end: null, durationLabel: '—', startLabel: '—', endLabel: '—' };
      const durationDays = parseInt(this.band?.duree_jours, 10) || 42;
      const start = new Date(startStr);
      if (Number.isNaN(start.getTime())) return { start: null, end: null, durationLabel: '—', startLabel: '—', endLabel: '—' };
      const end = new Date(start);
      end.setDate(start.getDate() + durationDays - 1);
      return {
        start,
        end,
        durationLabel: `${durationDays} j` ,
        startLabel: start.toLocaleDateString('fr-FR'),
        endLabel: end.toLocaleDateString('fr-FR')
      };
    },

    bandCalendarMonths() {
      const range = this.bandDateRange;
      if (!range.start || !range.end) return [];
      const highlights = this.calendarHighlights(range.start, range.end);
      const months = [];
      const cursor = new Date(range.start.getFullYear(), range.start.getMonth(), 1);
      const last = new Date(range.end.getFullYear(), range.end.getMonth(), 1);
      while (cursor <= last) {
        const year = cursor.getFullYear();
        const month = cursor.getMonth();
        const firstDay = new Date(year, month, 1);
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const startOffset = (firstDay.getDay() + 6) % 7; // Monday first
        const cells = [];
        for (let i = 0; i < startOffset; i += 1) cells.push({ empty: true, key: `${year}-${month}-empty-${i}` });
        for (let day = 1; day <= daysInMonth; day += 1) {
          const date = new Date(year, month, day);
          const key = date.toISOString().slice(0, 10);
          const events = highlights.get(key) || [];
          const inRange = date >= range.start && date <= range.end;
          const isStart = key === range.start.toISOString().slice(0, 10);
          const isEnd = key === range.end.toISOString().slice(0, 10);
          cells.push({
            empty: false,
            day,
            key,
            events,
            inRange,
            isStart,
            isEnd
          });
        }
        while (cells.length % 7 !== 0) {
          cells.push({ empty: true, key: `${year}-${month}-tail-${cells.length}` });
        }
        const monthLabel = firstDay.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
        months.push({ monthLabel, cells });
        cursor.setMonth(cursor.getMonth() + 1);
      }
      return months;
    },

    dashboardKeyEvents() {
      const events = [];
      const arrival = this.band?.date_arrivee;
      const initial = this.band?.nombre_initial || 0;

      if (arrival) {
        events.push({ id: 'arrivee', date: arrival, label: 'Arrivée du lot', details: initial ? `${initial} sujets` : null });
      }

      const durationDays = parseInt(this.band?.duree_jours, 10) || 42;
      if (arrival && durationDays) {
        const end = new Date(arrival);
        if (!Number.isNaN(end.getTime())) {
          end.setDate(end.getDate() + durationDays - 1);
          events.push({ id: 'fin-cycle', date: end.toISOString().slice(0, 10), label: 'Fin de cycle cible', details: `S${this.durationWeeks}` });
        }
      }

      if (this.optimalSellingDate) {
        events.push({
          id: 'vente-opt',
          date: this.optimalSellingDate,
          label: 'Vente optimale estimée',
          details: this.totalPredictedProfit ? `Marge ${this.formatCurrencyFCFA(this.totalPredictedProfit, 0)}` : null
        });
      }

      const nextWeek = this.nextAvailableWeek;
      if (arrival && nextWeek) {
        const nextDate = new Date(arrival);
        if (!Number.isNaN(nextDate.getTime())) {
          nextDate.setDate(nextDate.getDate() + (nextWeek - 1) * 7);
          events.push({ id: 'next-week', date: nextDate.toISOString().slice(0, 10), label: `S${nextWeek} à saisir`, details: 'Consos / poids hebdo' });
        }
      }

      const upcomingTreatment = [...(this.treatmentRecords || [])]
        .map((t, idx) => ({ ...t, _idx: idx, _date: new Date(t.fin || t.debut || NaN) }))
        .filter(t => !Number.isNaN(t._date.getTime()))
        .sort((a, b) => a._date - b._date)[0];
      if (upcomingTreatment) {
        events.push({
          id: `trait-${upcomingTreatment._idx}`,
          date: (upcomingTreatment.fin || upcomingTreatment.debut),
          label: upcomingTreatment.produit || 'Traitement',
          details: upcomingTreatment.maladie || 'Plan sanitaire'
        });
      }

      return events;
    },

    consumptionPerformance() {
      const population = Number(this.band?.nombre_initial || 0) || 0;
      const duration = this.durationWeeks;
      const actualByWeek = Array(duration).fill(null);
      const costByWeek = Array(duration).fill(null);

      this.consommations.forEach(c => {
        const w = c.semaine_production;
        if (!w || w < 1 || w > duration) return;
        const idx = w - 1;
        const kg = Number(c.kg || 0);
        const eau = Number(c.eau_litres || 0);
        const pu = Number(c.prix_unitaire || 0);
        const puEau = Number(c.prix_eau_unitaire || 0);
        actualByWeek[idx] = (actualByWeek[idx] || 0) + kg;
        costByWeek[idx] = (costByWeek[idx] || 0) + (kg * pu + eau * puEau);
      });

      const avgFeedPrice = this.averageUnitPrice('aliment');
      const avgWaterPrice = this.averageUnitPrice('eau');

      const ref = this.consumptionReference || [];
      const refKg = Array(duration).fill(null);
      const refCost = Array(duration).fill(null);

      for (let i = 0; i < duration; i += 1) {
        const refWeek = ref.find(r => r.week === i + 1);
        if (!refWeek) continue;
        refKg[i] = refWeek.aliment_kg || 0;
        const waterRef = refWeek.eau_litres || 0;
        refCost[i] = (avgFeedPrice || 0) * (refWeek.aliment_kg || 0) + (avgWaterPrice || 0) * waterRef;
      }

      const ratios = refKg.map((rk, i) => {
        const ak = actualByWeek[i];
        const rc = refCost[i];
        const ac = costByWeek[i];
        const consScore = rk && ak ? this.ratioScore(rk, ak) : null;
        const costScore = rc && ac ? this.ratioScore(rc, ac) : null;
        return { consScore, costScore };
      });

      const consValues = ratios.map(r => r.consScore).filter(v => v !== null);
      const costValues = ratios.map(r => r.costScore).filter(v => v !== null);
      const consAvg = consValues.length ? this.average(consValues) : null;
      const costAvg = costValues.length ? this.average(costValues) : null;
      const overall = (consAvg !== null || costAvg !== null) ? Math.round(((consAvg || 0) + (costAvg || 0)) / ((consAvg !== null && costAvg !== null) ? 2 : 1)) : null;

      // Expose ref total cost for other metrics (treatments / elementary expenses)
      this._lastRefCostTotal = refCost.reduce((s, v) => s + (Number(v) || 0), 0);

      return {
        consumption: consAvg !== null ? Math.round(consAvg) : null,
        cost: costAvg !== null ? Math.round(costAvg) : null,
        overall: overall,
        hasConsumptionData: consValues.length > 0,
        hasCostData: costValues.length > 0
      };
    },


    // Aggregate reference cost (sum of weekly reference costs calculated in consumptionPerformance)
    refTotalCost() {
      // Try to reuse cached computation from consumptionPerformance
      if (typeof this._lastRefCostTotal === 'number') return this._lastRefCostTotal;

      // Fallback: compute similar to consumptionPerformance
      const duration = this.durationWeeks;
      const avgFeedPrice = this.averageUnitPrice('aliment');
      const avgWaterPrice = this.averageUnitPrice('eau');
      const ref = this.consumptionReference || [];
      let total = 0;
      for (let i = 0; i < duration; i += 1) {
        const refWeek = ref.find(r => r.week === i + 1);
        if (!refWeek) continue;
        const rc = (avgFeedPrice || 0) * (refWeek.aliment_kg || 0) + (avgWaterPrice || 0) * (refWeek.eau_litres || 0);
        total += rc;
      }
      return total;
    },

    monthCalendar() {
      const now = new Date();
      const startMonth = new Date(now.getFullYear(), now.getMonth(), 1);
      const endMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);

      const startWeekday = (startMonth.getDay() + 6) % 7; // Monday=0
      const totalDays = endMonth.getDate();

      const cells = [];
      for (let i = 0; i < startWeekday; i += 1) {
        cells.push({ date: null });
      }

      let weekRangeStart = null;
      let weekRangeEnd = null;
      const lastFilled = [...this.consommations]
        .filter(c => c.semaine_production)
        .sort((a, b) => b.semaine_production - a.semaine_production)[0];
      if (lastFilled?.semaine_production && this.band?.date_arrivee) {
        const bandStart = new Date(this.band.date_arrivee);
        if (!Number.isNaN(bandStart.getTime())) {
          bandStart.setHours(0, 0, 0, 0);
          weekRangeStart = new Date(bandStart);
          weekRangeStart.setDate(bandStart.getDate() + (lastFilled.semaine_production - 1) * 7);
          weekRangeEnd = new Date(weekRangeStart);
          weekRangeEnd.setDate(weekRangeStart.getDate() + 6);
        }
      }

      for (let d = 1; d <= totalDays; d += 1) {
        const date = new Date(now.getFullYear(), now.getMonth(), d);
        date.setHours(0, 0, 0, 0);
        const isToday = this.isSameDay(date, now);
        const isStart = weekRangeStart ? this.isSameDay(date, weekRangeStart) : false;
        const isEnd = weekRangeEnd ? this.isSameDay(date, weekRangeEnd) : false;
        const isWeekRange = weekRangeStart && weekRangeEnd && date >= weekRangeStart && date <= weekRangeEnd;
        const isWeekStart = weekRangeStart ? this.isSameDay(date, weekRangeStart) : false;
        const isWeekEnd = weekRangeEnd ? this.isSameDay(date, weekRangeEnd) : false;
        cells.push({ date, day: d, isToday, isStart, isEnd, isWeekRange, isWeekStart, isWeekEnd });
      }

      while (cells.length % 7 !== 0) {
        cells.push({ date: null });
      }

      const monthLabel = startMonth.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
      return { monthLabel, cells };
    },

    criticalAlerts() {
      const alerts = [];

      const lastCons = this.getLastWeekStats();
      if (lastCons?.refCost && lastCons.actualCost > lastCons.refCost * 1.1) {
        alerts.push({ id: 'cost', text: `S${lastCons.week}: coût au-dessus de la réf (${this.formatCurrencyFCFA(lastCons.actualCost)} vs ${this.formatCurrencyFCFA(lastCons.refCost)})` });
      }
      if (lastCons?.refKg && lastCons.actualKg > lastCons.refKg * 1.1) {
        alerts.push({ id: 'cons-high', text: `S${lastCons.week}: consommation élevée vs réf (${lastCons.actualKg} kg)` });
      }
      if (lastCons?.refKg && lastCons.actualKg < lastCons.refKg * 0.9) {
        alerts.push({ id: 'cons-low', text: `S${lastCons.week}: consommation faible vs réf (${lastCons.actualKg} kg)` });
      }

      if (this.animalInfos.length) {
        const lastAnimal = [...this.animalInfos].sort((a, b) => (b.semaine_production || 0) - (a.semaine_production || 0))[0];
        const ref = this.getMortalityRef(lastAnimal.semaine_production);
        const rate = this.calculateWeeklyMortalityRate(lastAnimal);
        if (rate > ref.high) {
          alerts.push({ id: 'mortality', text: `S${lastAnimal.semaine_production}: mortalité ${rate}% > réf (${ref.high}%)` });
        }
      }

      if (this.survivalPerformance < 85) {
        alerts.push({ id: 'survival', text: `Survie faible: ${this.survivalPerformance}%` });
      }

      const missingConso = [];
      const missingAnimal = [];
      for (let w = 1; w <= this.currentProductionWeek; w += 1) {
        const hasConso = this.consommations.some(c => c.semaine_production === w);
        const hasAnimal = this.animalInfos.some(i => i.semaine_production === w);
        if (!hasConso) missingConso.push(w);
        if (!hasAnimal) missingAnimal.push(w);
      }
      if (missingConso.length) {
        alerts.push({ id: 'missing-conso', text: `Semaines sans conso: S${missingConso.join(', S')}` });
      }
      if (missingAnimal.length) {
        alerts.push({ id: 'missing-animal', text: `Semaines sans infos animaux: S${missingAnimal.join(', S')}` });
      }

      const consoNoAnimal = this.consommations
        .filter(c => c.semaine_production && !this.animalInfos.some(i => i.semaine_production === c.semaine_production))
        .map(c => c.semaine_production);
      if (consoNoAnimal.length) {
        alerts.push({ id: 'conso-no-animal', text: `Conso ajoutée mais infos animaux manquantes: S${[...new Set(consoNoAnimal)].join(', S')}` });
      }

      return alerts;
    },

    lastWeekAdvice() {
      const stats = this.getLastWeekStats();
      if (!stats) return [];
      const advices = [];

      if (stats.refKg > 0) {
        if (stats.actualKg > stats.refKg * 1.05) {
          advices.push({
            level: 'warning',
            text: `S${stats.week}: Consommation supérieure à la référence, réduire légèrement la ration et surveiller l'appétit.`
          });
        } else if (stats.actualKg < stats.refKg * 0.95) {
          advices.push({
            level: 'info',
            text: `S${stats.week}: Consommation inférieure à la référence, augmenter progressivement et prévoir un stimulant d'appétit.`
          });
        }
      }

      if (stats.refCost > 0) {
        if (stats.actualCost > stats.refCost * 1.05) {
          advices.push({
            level: 'warning',
            text: `S${stats.week}: Coût au-dessus de la référence, vérifier prix d'achat et ration pour réduire les dépenses.`
          });
        } else if (stats.actualCost < stats.refCost * 0.95) {
          advices.push({
            level: 'info',
            text: `S${stats.week}: Coût en dessous de la référence, OK mais garder la qualité d'aliment et d'eau.`
          });
        }
      }

      return advices;
    },

    messageBuckets() {
      const dismissed = new Set(this.dismissedMessageIds || []);

      const critical = (this.criticalAlerts || []).map(alert => ({
        id: `crit-${alert.id}`,
        text: alert.text
      }));

      const problem = (this.lastWeekAdvice || []).map((adv, idx) => ({
        id: `prob-${adv.level || 'info'}-${idx}`,
        text: adv.text
      }));

      const good = [];
      if (this.survivalPerformance >= 90) {
        good.push({ id: 'good-survival', text: `Survie solide: ${this.survivalPerformance}%` });
      }
      if (this.gainsComputed?.delta > 0) {
        good.push({
          id: 'good-gains',
          text: `Gains au-dessus de la référence de ${this.formatCurrencyFCFA(this.gainsComputed.delta, 0)}`
        });
      }

      const filterDismissed = list => list.filter(m => !dismissed.has(m.id));
      return {
        critical: filterDismissed(critical),
        problem: filterDismissed(problem),
        good: filterDismissed(good)
      };
    },

    hasAnyMessages() {
      const buckets = this.messageBuckets;
      return buckets.critical.length + buckets.problem.length + buckets.good.length > 0;
    },

    currentMessages() {
      const buckets = this.messageBuckets;
      return buckets[this.activeMessageTab] || [];
    },

    activeMessageLabel() {
      if (this.activeMessageTab === 'critical') return 'Alertes critiques';
      if (this.activeMessageTab === 'problem') return 'Points à surveiller';
      if (this.activeMessageTab === 'good') return 'Bonnes nouvelles';
      return 'Messages';
    },

    messageIcon() {
      if (this.activeMessageTab === 'critical') return '⚠️';
      if (this.activeMessageTab === 'problem') return '❗';
      if (this.activeMessageTab === 'good') return '✅';
      return 'ℹ️';
    },

    messageCounts() {
      const b = this.messageBuckets;
      return {
        critical: b.critical.length,
        problem: b.problem.length,
        good: b.good.length
      };
    },

    availableMessageTypes() {
      return ['critical', 'problem', 'good'].filter(t => this.messageCounts[t] > 0);
    }
  },
  
  methods: {
    toggleMessageTab(tab) { return messageMethods.toggleMessageTab(this, tab); },
    dismissMessage(id) { return messageMethods.dismissMessage(this, id); },
    dismissMessageBucket(tab) { return messageMethods.dismissMessageBucket(this, tab); },
    ensureActiveMessageTab() { return messageMethods.ensureActiveMessageTab(this); },

    goHome() {
      if (this.$router) {
        this.$router.push('/home');
      } else {
        this.selectTab('dashboard');
      }
    },

    openExpenseDrawer(item) {
      this.expenseSelected = item;
      this.expenseForm.tache = item?.name || '';
      this.expenseDrawerOpen = true;
    },

    getSearchItems() {
      return [
        { key: 'tab-dashboard', label: 'Aller Dashboard', type: 'Onglet', action: 'tab', tab: 'dashboard' },
        { key: 'tab-consommation', label: 'Consommation', type: 'Onglet', action: 'tab', tab: 'consommation', hint: 'Semaine, kg, eau' },
        { key: 'tab-predictions', label: 'Prédictions', type: 'Onglet', action: 'tab', tab: 'predictions', hint: 'Courbes prévisionnelles' },
        { key: 'tab-kpi', label: 'KPIs', type: 'Onglet', action: 'tab', tab: 'kpi', hint: 'Indicateurs clés' },
        { key: 'tab-traitements', label: 'Traitements', type: 'Onglet', action: 'tab', tab: 'traitements', hint: 'Catalogue + formulaire' },
        { key: 'tab-animaux', label: 'Animaux', type: 'Onglet', action: 'tab', tab: 'animaux', hint: 'Infos hebdo' },
        { key: 'tab-finances-dep', label: 'Finances - Dépenses', type: 'Onglet', action: 'tab', tab: 'finances', financeSubTab: 'depenses', hint: 'Cartes + tiroir' },
        { key: 'tab-finances-gains', label: 'Finances - Gains', type: 'Onglet', action: 'tab', tab: 'finances', financeSubTab: 'gains', hint: 'Ventes, subventions' },
        { key: 'tab-chatbot', label: 'Chatbot', type: 'Onglet', action: 'tab', tab: 'chatbot', hint: 'Assistant IA' },
        { key: 'tab-infos', label: 'Infos', type: 'Onglet', action: 'tab', tab: 'infos', hint: 'Détails de la bande' },
        { key: 'action-add-expense', label: 'Ajouter une dépense', type: 'Action', action: 'openExpense', hint: 'Ouvre le tiroir dépenses' },
        { key: 'action-add-treatment', label: 'Ajouter un traitement', type: 'Action', action: 'openTreatment', hint: 'Accéder au formulaire' }
      ];
    },

    updateSearchResults() {
      const q = (this.searchQuery || '').trim().toLowerCase();
      if (!q) {
        this.searchResults = [];
        this.searchFocusedIndex = 0;
        return;
      }
      const pool = this.getSearchItems();
      this.searchResults = pool
        .filter(item => item.label.toLowerCase().includes(q) || (item.hint && item.hint.toLowerCase().includes(q)))
        .slice(0, 8);
      this.searchFocusedIndex = 0;
    },

    handleSearchKeydown(evt) {
      if (!this.searchResults.length) return;
      if (evt.key === 'ArrowDown') {
        evt.preventDefault();
        this.searchFocusedIndex = (this.searchFocusedIndex + 1) % this.searchResults.length;
      } else if (evt.key === 'ArrowUp') {
        evt.preventDefault();
        this.searchFocusedIndex = (this.searchFocusedIndex - 1 + this.searchResults.length) % this.searchResults.length;
      } else if (evt.key === 'Enter') {
        evt.preventDefault();
        const target = this.searchResults[this.searchFocusedIndex];
        this.executeSearchResult(target);
      } else if (evt.key === 'Escape') {
        this.closeSearch(true);
      }
    },

    executeSearchResult(item) {
      if (!item) return;
      if (item.action === 'tab') {
        this.selectTab(item.tab);
        if (item.financeSubTab) this.financeSubTab = item.financeSubTab;
      } else if (item.action === 'openExpense') {
        this.financeSubTab = 'depenses';
        this.selectTab('finances');
        this.openExpenseDrawer(this.expenseCatalog[0] || null);
      } else if (item.action === 'openTreatment') {
        this.selectTab('traitements');
      }
      this.searchResults = [];
      this.searchQuery = '';
    },

    closeSearch(clear = false) {
      setTimeout(() => {
        this.searchResults = [];
        this.searchFocusedIndex = 0;
        if (clear) this.searchQuery = '';
      }, 100);
    },

    closeExpenseDrawer() { return depensesMethods.closeExpenseDrawer(this); },

    expenseStorageKey() { return depensesMethods.expenseStorageKey(this); },

    treatmentStorageKey() { return traitementsMethods.treatmentStorageKey(this); },

    loadExpenseRecordsFromStorage() { return depensesMethods.loadExpenseRecordsFromStorage(this); },

    loadTreatmentRecordsFromStorage() { return traitementsMethods.loadTreatmentRecordsFromStorage(this); },

    saveExpense() { return depensesMethods.saveExpense(this); },

    getExpenseImage(pathOrName) { return depensesMethods.getExpenseImage(this, pathOrName); },

    openExpenseDrawer(item) { return depensesMethods.openExpenseDrawer(this, item); },

    formatNumber(value, decimals = 2) { return tabUtils.formatNumber(value, decimals); },
    formatCurrencyFCFA(value, decimals = 0) { return tabUtils.formatCurrencyFCFA(value, decimals); },
    formatWeekRange(startDate, week) { return tabUtils.formatWeekRange(startDate, week); },

    formatPercent(val) { return tabUtils.formatPercent(val); },

    showBandPerfDetails() {
      const perf = this.serverPerformance || {};
      const msg = `Performance: ${perf.performance_percent ?? '—'}%\nSubscores: ${perf.subscores ? JSON.stringify(perf.subscores) : '—'}`;
      alert(msg);
    },

    updateCostPreview() { return consommationMethods.updateCostPreview(this); },

    averageUnitPrice(type) {
      const values = this.consommations
        .map(c => type === 'eau' ? Number(c.prix_eau_unitaire || 0) : Number(c.prix_unitaire || 0))
        .filter(v => Number.isFinite(v) && v > 0);
      if (!values.length) return 0;
      return values.reduce((a, b) => a + b, 0) / values.length;
    },

    ratioScore(refValue, actualValue) {
      // Return null when comparison is not meaningful (avoid treating missing data as perfect)
      if (refValue == null || refValue <= 0) return null;
      if (actualValue == null || actualValue <= 0) return null;
      if (actualValue <= refValue) return 100;
      return Math.max(0, Math.min(100, Math.round((refValue / actualValue) * 100)));
    },

    average(arr) {
      if (!arr.length) return 0;
      return arr.reduce((a, b) => a + b, 0) / arr.length;
    },

    getLastWeekStats() {
      if (!this.consommations.length) return null;
      const last = [...this.consommations]
        .filter(c => c.semaine_production)
        .sort((a, b) => b.semaine_production - a.semaine_production)[0];
      if (!last) return null;

      const week = last.semaine_production;
      const refWeek = (this.consumptionReference || []).find(r => r.week === week);
      const avgFeed = this.averageUnitPrice('aliment');
      const avgWater = this.averageUnitPrice('eau');

      const refKg = refWeek?.aliment_kg || 0;
      const refEau = refWeek?.eau_litres || 0;
      const refCost = Math.round((avgFeed || 0) * refKg + (avgWater || 0) * refEau);

      const actualKg = Number(last.kg || 0);
      const actualEau = Number(last.eau_litres || 0);
      const actualCost = Math.round(actualKg * (last.prix_unitaire || 0) + actualEau * (last.prix_eau_unitaire || 0));

      return { week, refKg, refCost, actualKg, actualCost };
    },

    getDateForWeek(week) {
      if (!this.band?.date_arrivee) return new Date().toISOString().slice(0, 10);
      const start = new Date(this.band.date_arrivee);
      start.setDate(start.getDate() + (week - 1) * 7);
      return start.toISOString().slice(0, 10);
    },
    parseDate(str) { return tabUtils.parseDate(str); },
    isSameDay(a, b) { return tabUtils.isSameDay(a, b); },
    getFilledWeeksMap() { return tabUtils.getFilledWeeksMapFrom(this.consommations); },
    scrollToConsumptionForm() { return tabUtils.scrollToConsumptionForm(); },

    recommendedDose(t) { return traitementsMethods.recommendedDose(this, t); },

    getMedocImage(relPath) {
      try {
        return new URL(relPath, import.meta.url).href;
      } catch (e) {
        return this.medocPlaceholder;
      }
    },

    onMedocImgError(evt) {
      evt.target.src = this.medocPlaceholder;
    },

    prefillTreatment(t) { return traitementsMethods.prefillTreatment(this, t); },

    resetTreatmentForm() { return traitementsMethods.resetTreatmentForm(this); },

    addTreatmentRecord() { return traitementsMethods.addTreatmentRecord(this); },

    editWeek(row) {
      if (!row?.consumptionId) return;
      const cons = this.consommations.find(c => c.id === row.consumptionId);
      if (cons) this.startEditConsumption(cons);
    },

    async deleteWeek(row) {
      if (!row?.consumptionId) return;
      const cons = this.consommations.find(c => c.id === row.consumptionId);
      if (cons) await this.deleteConsumption(cons);
    },

    async fetchBand() {
      try {
        const storedBand = localStorage.getItem('current_band');
        
        if (!storedBand) {
          this.band = null;
          this.id = null;
          return;
        }
        
        let bandData;
        try {
          bandData = JSON.parse(storedBand);
        } catch (e) {
          console.error('Error parsing band data:', e);
          this.band = null;
          this.id = null;
          return;
        }
        
        this.band = bandData;
        
        // Récupérer l'ID correctement
        this.id = bandData?.id || bandData?.bande_id || null;
        
        console.log('Band data from localStorage:', bandData);
        console.log('Original ID from band data:', this.id);
        
        // Nettoyer l'ID pour l'API
        if (this.id) {
          // Si l'ID est un objet, extraire la valeur
          if (typeof this.id === 'object') {
            this.id = this.id.id || this.id.value || null;
          }
          
          // Si c'est une string avec ":", prendre seulement la première partie
          if (typeof this.id === 'string') {
            this.id = this.id.split(':')[0].trim();
            
            // Convertir en nombre si possible
            const numericId = parseInt(this.id);
            if (!isNaN(numericId)) {
              this.id = numericId;
            }
          }
        }
        
        console.log('Final cleaned band ID for API:', this.id, 'Type:', typeof this.id);

        // Charger les dépenses et traitements locaux liés à cette bande
        this.loadExpenseRecordsFromStorage();
        this.loadTreatmentRecordsFromStorage();
        
        // Charger les données de la BD après avoir l'ID
        await this.loadBandDataFromDB();
        this.resetAnimalInfoForm();
        
      } catch (e) {
        console.error("fetchBand error:", e);
        this.band = null;
        this.id = null;
      }
    },

    async loadBandDataFromDB() {
      try {
        if (!this.id) return;
        
        // Charger les données complètes de la bande depuis l'API
        const response = await fetch(`http://localhost:5000/bandes/${this.id}`, {
          credentials: 'include'
        });
        
        if (response.ok) {
          const bandData = await response.json();
          
          // Fusionner les données du localStorage avec celles de la BD
          this.band = { ...this.band, ...bandData };

          // Calculer les semaines déjà prises pour désactiver la sélection
          this.filledWeeks = this.getFilledWeeksMap();
          
          // Mettre à jour les trends avec des données réelles
          this.updateTrendsFromData();
          
          // Fetch server-side performance for this band and use it when available
          try {
            const perfResp = await fetch(`http://localhost:5000/dashboard/bande/details/${this.id}`, { credentials: 'include' });
            if (perfResp.ok) {
              const perfJson = await perfResp.json().catch(() => null);
              if (perfJson && perfJson.performance) {
                this.serverPerformance = perfJson.performance;
                try { localStorage.setItem(`band_performance_${this.id}`, JSON.stringify(this.serverPerformance)); } catch (e) { /* ignore */ }
                // Also merge into global map stored in localStorage so Home and others read the same values
                try {
                  const existing = localStorage.getItem('band_performance_map');
                  const parsed = existing ? JSON.parse(existing) : {};
                  const perfValue = typeof this.serverPerformance.performance_percent === 'number' ? this.serverPerformance.performance_percent : null;
                  const merged = { ...(parsed || {}) };
                  if (perfValue !== null) merged[this.id] = perfValue;
                  if (this.serverPerformance.subscores) merged[`components_${this.id}`] = this.serverPerformance.subscores;
                  localStorage.setItem('band_performance_map', JSON.stringify(merged));
                } catch (e) { /* ignore */ }
                // Dispatch a custom event so same-tab listeners (Home) can react immediately
                try { window.dispatchEvent(new CustomEvent('bandPerformanceUpdated', { detail: { id: this.id, performance: this.serverPerformance } })); } catch (e) { /* ignore */ }
                // Also warn if local cached map (Home) has a different value
                try {
                  const cached = localStorage.getItem(`band_performance_${this.id}`);
                  if (cached) {
                    const parsed = JSON.parse(cached);
                    console.log('Server performance cached for band', this.id, parsed);
                  }
                } catch (e) { /* ignore */ }
              }
            }
          } catch (e) {
            console.warn('Erreur fetch server performance:', e);
          }

          console.log('Band data loaded from DB:', bandData);
        }
      } catch (error) {
        console.warn('Error loading band data from DB:', error);
      }
    },

    updateTrendsFromData() {
      // Calculer des trends basées sur les données réelles
      if (this.band?.poids_moyen_initial) {
        this.trends.poids = this.calculateWeightTrend();
        this.trends.cout = this.calculateCostTrend();
        this.trends.mortalite = this.calculateMortalityTrend();
        this.trends.ic = this.calculateICTrend();
      }
    },

    calculateWeightTrend() {
      // Simuler un trend basé sur les données
      if (!this.band?.poids_moyen_initial) return 0;
      
      // Exemple : si le poids moyen est bon (> 2.5kg), trend positif
      return this.band.poids_moyen_initial > 2.5 ? 2.5 : -1.0;
    },

    calculateCostTrend() {
      // Calculer basé sur le coût total
      const totalConsommations = this.totalCost;
      // Exemple : si coût < 500 FCFA, trend négatif (bon)
      return totalConsommations < 500 ? -1.2 : 3.5;
    },

    calculateMortalityTrend() {
      if (!this.band?.nombre_initial || this.band.nombre_initial === 0) return 0;
      
      const mortalityRate = ((this.band.nombre_morts_totaux || 0) / this.band.nombre_initial) * 100;
      // Exemple : si mortalité < 5%, trend bas
      return mortalityRate < 5 ? 0.5 : 2.5;
    },

    async loadAnimalInfos() { return await animauxMethods.loadAnimalInfos(this); },

    getMortalityRef(week) { return animauxMethods.getMortalityRef(this, week); },
    getWeightRef(week) { return animauxMethods.getWeightRef(this, week); },
    weightRefDisplay(week) { return animauxMethods.weightRefDisplay(this, week); },
    mortalityRefDisplay(week) { return animauxMethods.mortalityRefDisplay(this, week); },
    calculateWeeklyMortalityRate(info) { return animauxMethods.calculateWeeklyMortalityRate(this, info); },
    async loadAnimalInfos() { return await animauxMethods.loadAnimalInfos(this); },
    resetAnimalInfoForm() { return animauxMethods.resetAnimalInfoForm(this); },
    startEditAnimalInfo(info) { return animauxMethods.startEditAnimalInfo(this, info); },
    async saveAnimalInfo() { return await animauxMethods.saveAnimalInfo(this); },
    async deleteAnimalInfo(info) { return await animauxMethods.deleteAnimalInfo(this, info); },

    calculateICTrend() {
      // Indice de consommation (plus bas = mieux)
      const totalConsommations = this.totalCost;
      const currentAnimals = this.currentAnimals;
      
      if (currentAnimals === 0 || totalConsommations === 0) return 0;
      
      const ic = totalConsommations / currentAnimals;
      // Exemple : si IC < 2, trend négatif (bon)
      return ic < 2 ? -0.8 : 1.5;
    },

    async calculateKPI() {
      try {
        if (!this.id) return;
        
        const data = await fetch(`http://localhost:5000/bandes/${this.id}`, {
          credentials: 'include'
        }).then(res => res.ok ? res.json() : null);
        
        if (!data) {
          this.kpi = {
            poids_moyen: this.band?.poids_moyen_initial || null,
            cout_total: 0,
            taux_mortalite: this.band?.nombre_initial > 0 ? 
              ((this.band?.nombre_morts_totaux || 0) / this.band?.nombre_initial * 100).toFixed(2) : 0,
            ic: 0,
          };
          return;
        }
        
        const total_animaux = data.total_animaux_actuels || 
          (data.nombre_initial || 0) + (data.nbre_ajoute || 0) - (data.nombre_morts_totaux || 0);
        
        this.kpi = {
          poids_moyen: data.poids_moyen_initial || null,
          cout_total: 0,
          taux_mortalite: total_animaux > 0 ? 
            ((data.nombre_morts_totaux || 0) / (data.nombre_initial || 1) * 100).toFixed(2) : 0,
          ic: 0,
        };
      } catch (e) {
        console.warn("calculateKPI error:", e);
        this.kpi = {
          poids_moyen: "—",
          cout_total: "—",
          taux_mortalite: "—",
          ic: "—"
        };
      }
    },

    async loadConsommations() { return await consommationMethods.loadConsommations(this); },

    async loadTreatmentsFromServer() { return await traitementsMethods.fetchTreatmentRecordsFromServer(this); },

    async loadExpensesFromServer() { return await depensesMethods.fetchExpenseRecordsFromServer(this); },

    async fetchTabData(tab) {
      // Éviter les appels en double
      if (this._fetchingTab === tab) {
        console.log(`⏳ Données ${tab} déjà en cours de chargement`);
        return;
      }
      
      this._fetchingTab = tab;
      
      try {
        if (!this.id) {
          console.warn('No band ID available');
          return;
        }

        const wantsConsommations = ['consommation', 'dashboard', 'finances', 'kpi', 'predictions'].includes(tab);
        const wantsAnimalInfos = ['animaux', 'finances', 'dashboard', 'kpi', 'predictions'].includes(tab);
        const wantsTreatments = ['sante', 'dashboard', 'kpi', 'finances'].includes(tab);
        const wantsExpenses = ['finances', 'dashboard', 'kpi'].includes(tab);

        const tasks = [];
        const shouldFetchCons = wantsConsommations && (tab === 'consommation' || this.consommations.length === 0);
        const shouldFetchAnimals = wantsAnimalInfos && (tab === 'animaux' || this.animalInfos.length === 0);
        const shouldFetchTreatments = wantsTreatments && (tab === 'sante' ? (this.santeSubTab === 'traitements' || this.treatmentRecords.length === 0) : this.treatmentRecords.length === 0);
        const shouldFetchExpenses = wantsExpenses && (tab === 'finances' ? (this.financeSubTab === 'depenses' || this.expenseRecords.length === 0) : this.expenseRecords.length === 0);

        if (shouldFetchCons) tasks.push(this.loadConsommations());
        if (shouldFetchAnimals) tasks.push(this.loadAnimalInfos());
        if (shouldFetchTreatments) tasks.push(this.loadTreatmentsFromServer());
        if (shouldFetchExpenses) tasks.push(this.loadExpensesFromServer());

        if (tasks.length) {
          await Promise.all(tasks);
        }
        // ... autres onglets ...
      } catch (error) {
        console.warn("❌ Erreur fetchTabData:", error);
        this.consommations = [];
      } finally {
        this._fetchingTab = null;
      }
    },
    

    async addConsumption() { return await consommationMethods.addConsumption(this); },

    startEditConsumption(cons) { return consommationMethods.startEditConsumption(this, cons); },

    resetConsumptionForm() { return consommationMethods.resetConsumptionForm(this); },


    async deleteConsumption(cons) { return await consommationMethods.deleteConsumption(this, cons); },

    // Chatbot methods delegated to helper
    async analyserElevage() { return await chatbotMethods.analyserElevage(this); },
    async sendMessage() { return await chatbotMethods.sendMessage(this); },

    dismissChatMessage(index) { return messageMethods.dismissChatMessage(this, index); },

    selectTab(tab) {
      this.activeTab = tab;
      this.fetchTabData(tab);
    },

    openSettings() {
      console.log("Ouverture des paramètres");
    },
    
    formatDate(dateString) {
      if (!dateString) return '—';
      const date = new Date(dateString);
      return date.toLocaleDateString('fr-FR');
    },
    
    generatePredictions() { return predictionsMethods.generatePredictions(this); },
    
    calculateWeightIncrease(day) { return predictionsMethods.calculateWeightIncrease(day, this.predictionModel); },
    calculateAverageConsumption() { return predictionsMethods.calculateAverageConsumptionFrom(this); },
    getAverageCostPerKg() { return predictionsMethods.getAverageCostPerKgFrom(this); },
    getPricePerKg() { return predictionsMethods.getPricePerKgFrom(this); },

    calendarHighlights(startDate, endDate) {
      const map = new Map();
      const add = (dateVal, label, type = 'event') => {
        if (!dateVal) return;
        const d = new Date(dateVal);
        if (Number.isNaN(d.getTime())) return;
        const iso = d.toISOString().slice(0, 10);
        if (!map.has(iso)) map.set(iso, []);
        map.get(iso).push({ label, type });
      };

      add(startDate, 'Arrivée', 'start');
      add(endDate, 'Fin de bande', 'end');
      if (this.optimalSellingDate) add(this.optimalSellingDate, 'Vente optimale', 'sale');

      (this.consommations || []).forEach(c => add(c.date, 'Consommation', 'consumption'));
      (this.animalInfos || []).forEach(info => {
        if (!info?.semaine_production || !startDate) return;
        const d = new Date(startDate);
        d.setDate(d.getDate() + (info.semaine_production - 1) * 7);
        add(d, 'Pesée', 'weigh');
      });
      (this.treatmentRecords || []).forEach(t => {
        add(t.debut, 'Traitement', 'treat');
        add(t.fin, 'Fin traitement', 'treat');
      });

      if (startDate && endDate) {
        const duration = Math.max(1, Math.round((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1);
        const weeks = Math.ceil(duration / 7);
        for (let i = 1; i <= weeks; i += 1) {
          const d = new Date(startDate);
          d.setDate(d.getDate() + i * 7 - 1);
          add(d, 'Nettoyage', 'maintenance');
        }
      }

      return map;
    },

    findOptimalSellingDate() { return predictionsMethods.findOptimalSellingDateFrom(this.predictions); },
    getObservedWeightForPredictions() { return predictionsMethods.getObservedWeightForPredictions(this); },
    
    // Utility methods
    getTrendClass(type) {
      const trendValue = this.trends[type];
      if (typeof trendValue !== 'number') return 'neutral';
      if (trendValue > 0) return 'positive';
      if (trendValue < 0) return 'negative';
      return 'neutral';
    },
    
    getMarginClass(margin) {
      return margin > 0 ? 'positive' : margin < 0 ? 'negative' : 'neutral';
    },
    
    getProfitClass(profit) {
      return profit > 0 ? 'positive' : profit < 0 ? 'negative' : 'neutral';
    },
    
    getROIClass(roi) {
      return roi > 15 ? 'good' : roi > 5 ? 'medium' : 'low';
    }
  },
  
  mounted() {
    console.log('Component mounted');
    
    this.fetchBand().then(() => {
      // Une fois la bande chargée, charger les consommations
      this.fetchTabData(this.activeTab);
    });
  },
  
  beforeUnmount() {
    // Rien à nettoyer : les composants enfants gèrent leurs propres graphiques
  }
};
</script>

<style src="../../css/chart.css" type="text/css"></style>
<style src="../../css/band.css" type="text/css"></style>