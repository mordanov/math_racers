# Graph Report - .  (2026-10-10)

## Corpus Check
- 256 files · ~87,455 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1154 nodes · 1744 edges · 113 communities (105 shown, 8 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 192 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Auth & Achievement Schemas|Auth & Achievement Schemas]]
- [[_COMMUNITY_Core DB Models|Core DB Models]]
- [[_COMMUNITY_Avatar Domain Service|Avatar Domain Service]]
- [[_COMMUNITY_UI Button & Sound|UI Button & Sound]]
- [[_COMMUNITY_Account Repository|Account Repository]]
- [[_COMMUNITY_Frontend Dependencies|Frontend Dependencies]]
- [[_COMMUNITY_Achievements API Client|Achievements API Client]]
- [[_COMMUNITY_ADR Architecture Docs|ADR Architecture Docs]]
- [[_COMMUNITY_Achievement Evaluation|Achievement Evaluation]]
- [[_COMMUNITY_Domain Module Files|Domain Module Files]]
- [[_COMMUNITY_Statistics Repository|Statistics Repository]]
- [[_COMMUNITY_Parent Dashboard|Parent Dashboard]]
- [[_COMMUNITY_Race Engine|Race Engine]]
- [[_COMMUNITY_Badges & Results|Badges & Results]]
- [[_COMMUNITY_Math Generator|Math Generator]]
- [[_COMMUNITY_Avatar Repository|Avatar Repository]]
- [[_COMMUNITY_Child Profiles Backend|Child Profiles Backend]]
- [[_COMMUNITY_Avatar API Client|Avatar API Client]]
- [[_COMMUNITY_Race Screen Tests|Race Screen Tests]]
- [[_COMMUNITY_Notification Toast|Notification Toast]]
- [[_COMMUNITY_TS Compiler Config|TS Compiler Config]]
- [[_COMMUNITY_Avatar Creator & Offline|Avatar Creator & Offline]]
- [[_COMMUNITY_Difficulty Tiers|Difficulty Tiers]]
- [[_COMMUNITY_ESLint Config|ESLint Config]]
- [[_COMMUNITY_Child Profiles API|Child Profiles API]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]

## God Nodes (most connected - your core abstractions)
1. `Base` - 21 edges
2. `StatisticsDomainService` - 20 edges
3. `PermissionError` - 20 edges
4. `APIClient` - 19 edges
5. `SQLAlchemyAvatarRepository` - 19 edges
6. `SQLAlchemyStatisticsRepository` - 18 edges
7. `get_config()` - 18 edges
8. `compilerOptions` - 17 edges
9. `StatisticsRepository` - 17 edges
10. `AvatarRepository` - 17 edges

## Surprising Connections (you probably didn't know these)
- `CLAUDE.md Behavioral Guidelines` --semantically_similar_to--> `SpecKit Constitution`  [INFERRED] [semantically similar]
  CLAUDE.md → initial_spec/speckit_constitution.md
- `_run_pipeline()` --calls--> `type`  [INFERRED]
  backend/app/avatars/generation_service.py → frontend/package.json
- `Frontend index.html` --implements--> `ADR-004 Frontend Architecture`  [INFERRED]
  frontend/index.html → initial_spec/ADR/ADR-004.md
- `pnpm Workspace Config` --implements--> `ADR-004 Frontend Architecture`  [INFERRED]
  frontend/pnpm-workspace.yaml → initial_spec/ADR/ADR-004.md
- `SDD Sprint 1 Frontend Infrastructure` --implements--> `ADR-004 Frontend Architecture`  [INFERRED]
  .superpowers/sdd/2026-10-05-sprint-1-frontend-infrastructure/progress.md → initial_spec/ADR/ADR-004.md

## Hyperedges (group relationships)
- **ADR architecture set** — adr1, adr2, adr3, adr4, adr5 [EXTRACTED 0.90]
- **SDD sprint ledgers** — s1, s2, s3 [INFERRED 0.80]
- **Creative documentation set** — gdd, art, prompt, econ [INFERRED 0.75]

## Communities (113 total, 8 thin omitted)

### Community 0 - "Auth & Achievement Schemas"
Cohesion: 0.05
Nodes (36): AccountResponse, LoginRequest, RegisterRequest, AchievementListResponse, PlayerAchievementListResponse, AvatarCreationResponse, AvatarDetailResponse, AvatarListItem (+28 more)

### Community 1 - "Core DB Models"
Cohesion: 0.06
Nodes (28): Account, AccountRole, ApprovalStatus, RefreshToken, PlayerAchievement, Avatar, AvatarPortrait, GenerationJob (+20 more)

### Community 2 - "Avatar Domain Service"
Cohesion: 0.07
Nodes (27): AvatarDomainService, _enqueue_job(), _portrait_summary(), _to_detail(), _to_list_item(), _build_standings(), ChampionshipDomainService, _points_for_position() (+19 more)

### Community 3 - "UI Button & Sound"
Cohesion: 0.05
Nodes (33): Button(), ButtonProps, btn, onClick, playSfx, { rerender }, user, variantStyles (+25 more)

### Community 4 - "Account Repository"
Cohesion: 0.05
Nodes (11): AccountRepository, RefreshTokenRepository, AvatarRepository, ChampionshipRepository, SQLAlchemyChampionshipRepository, Protocol, RaceRepository, create_championship() (+3 more)

### Community 5 - "Frontend Dependencies"
Cohesion: 0.05
Nodes (39): dependencies, react, react-dom, react-router-dom, devDependencies, eslint, eslint-config-prettier, happy-dom (+31 more)

### Community 6 - "Achievements API Client"
Cohesion: 0.08
Nodes (20): AchievementListResponse, PlayerAchievementListResponse, Achievement, PlayerAchievement, ErrorState(), ErrorStateProps, getChildFriendlyMessage(), onRetry (+12 more)

### Community 7 - "ADR Architecture Docs"
Cohesion: 0.06
Nodes (34): ADR-001 Foundation Architecture, Clean Architecture / DDD / bounded contexts / event-driven, ADR-002 Backend Architecture, FastAPI backend with layered architecture, ADR-003 AI Architecture, AI pipeline: orchestrator, prompt builder, provider abstraction, prompt versioning, ADR-004 Frontend Architecture, React/TypeScript frontend: pages, features, engine layers (+26 more)

### Community 8 - "Achievement Evaluation"
Cohesion: 0.08
Nodes (12): AchievementDef, get_by_key(), AchievementDomainService, _count_races(), _pred_first_race(), _to_response(), AchievementRepository, SQLAlchemyAchievementRepository (+4 more)

### Community 9 - "Domain Module Files"
Cohesion: 0.08
Nodes (12): _calculate_xp_delta(), _compute_level(), ProgressionDomainService, _xp_to_next_level(), ProgressionRepository, SQLAlchemyProgressionRepository, LevelUpEvent, ProgressionResponse (+4 more)

### Community 10 - "Statistics Repository"
Cohesion: 0.11
Nodes (13): SQLAlchemyStatisticsRepository, _check_access(), export_my_csv(), get_avatar_statistics(), get_history(), get_my_history(), get_my_personal_records(), get_my_statistics() (+5 more)

### Community 11 - "Parent Dashboard"
Cohesion: 0.11
Nodes (19): fmtPct(), ParentDashboardPage(), mockSummary, fmtPct(), StatisticsPage(), mockHistory, mockStats, fetchPersonalRecords() (+11 more)

### Community 12 - "Race Engine"
Cohesion: 0.14
Nodes (16): config, { result }, useRaceEngine(), calculateMovement(), CHAMPIONSHIP_POINTS, createRaceEngine(), RaceEngine, RaceSummaryError (+8 more)

### Community 13 - "Badges & Results"
Cohesion: 0.11
Nodes (13): getBadgeUrl(), KNOWN_BADGE_IDS, Species, useVoicePlayer(), VoiceEmotion, ResultsRouteState, ResultsScreen(), SyncStatus (+5 more)

### Community 14 - "Math Generator"
Cohesion: 0.16
Nodes (17): clampTier(), selectTier(), compute(), generateProblemSet(), isDuplicate(), pickOperands(), pickOperation(), randomInt() (+9 more)

### Community 15 - "Avatar Repository"
Cohesion: 0.12
Nodes (9): SQLAlchemyAvatarRepository, create_avatar(), delete_avatar(), get_avatar(), get_job_status(), list_avatars(), patch_avatar(), regenerate_avatar() (+1 more)

### Community 16 - "Child Profiles Backend"
Cohesion: 0.10
Nodes (9): ChildProfileRepository, SQLAlchemyChildProfileRepository, get_child_profile(), get_child_profile_dependency(), Validate profile exists and belongs to the authenticated account.     Administra, FastAPI dependency: resolves and validates child profile ownership., create_child_profile(), delete_child_profile() (+1 more)

### Community 17 - "Avatar API Client"
Cohesion: 0.15
Nodes (17): createAvatar(), deleteAvatar(), patchAvatar(), pollGenerationJob(), regeneratePortrait(), AvatarCreationResponse, AvatarDetail, AvatarListItem (+9 more)

### Community 18 - "Race Screen Tests"
Cohesion: 0.10
Nodes (17): baseState, { container }, EngineReturn, hasTransition, playSfx, playVoice, problem, racingState (+9 more)

### Community 19 - "Notification Toast"
Cohesion: 0.15
Nodes (11): NotificationToast(), NotificationToastProps, onClose, { unmount }, user, typeColor, fill, XPBar() (+3 more)

### Community 20 - "TS Compiler Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 21 - "Avatar Creator & Offline"
Cohesion: 0.12
Nodes (14): { result }, useOffline(), ACCESSORIES_OPTIONS, AvatarCreatorPage(), CLOTHES_COLORS, EYE_COLORS, FUR_COLORS, HAIRSTYLES (+6 more)

### Community 22 - "Difficulty Tiers"
Cohesion: 0.14
Nodes (8): select_tier(), PlayerNotFoundError, PlayerDifficultyRepository, SQLAlchemyPlayerDifficultyRepository, DifficultyResponse, NotFoundError, get_difficulty(), patch_difficulty()

### Community 23 - "ESLint Config"
Cohesion: 0.12
Nodes (16): env, browser, es2022, extends, ignorePatterns, parser, parserOptions, ecmaVersion (+8 more)

### Community 24 - "Child Profiles API"
Cohesion: 0.16
Nodes (12): ChildProfileListResponse, createChildProfile(), fetchChildProfiles(), Account, ChildProfile, avatarCircleStyle, cardStyle, inputStyle (+4 more)

### Community 25 - "Community 25"
Cohesion: 0.15
Nodes (12): listAvatars(), MODES, SetupRouteState, btn, playSfx, published, user, createRaceSession() (+4 more)

### Community 26 - "Community 26"
Cohesion: 0.16
Nodes (12): AMBIENCE_FILES, applause, cheer, inst, { result }, { unmount }, useAmbienceManager(), buildParticipants() (+4 more)

### Community 27 - "Community 27"
Cohesion: 0.13
Nodes (14): btn, img, input, longName, onDelete, onFavourite, onRegenerate, onRename (+6 more)

### Community 28 - "Community 28"
Cohesion: 0.27
Nodes (12): _backoff_seconds(), _call_image_api(), _call_llm(), _generate_thumbnails(), _llm_user_prompt(), Execute the full avatar generation pipeline for a queued job., Return seconds to sleep before the next attempt. attempt_just_failed is 1-indexe, run_generation_job() (+4 more)

### Community 29 - "Community 29"
Cohesion: 0.18
Nodes (8): DuelConfig, BALANCED, PERSONALITIES, SLOW_STARTER, SPEEDSTER, STEADY, UNPREDICTABLE, ParticipantConfig

### Community 30 - "Community 30"
Cohesion: 0.24
Nodes (7): AchievementToast(), Props, SFX_FILES, SfxName, inst, { result }, useSfxPlayer()

### Community 31 - "Community 31"
Cohesion: 0.18
Nodes (4): ApproveAccountUseCase, ListAccountsUseCase, approve_account(), list_accounts()

### Community 32 - "Community 32"
Cohesion: 0.29
Nodes (7): useAuth(), RequireAuth(), RequireParent(), LoadingSpinner(), LoadingSpinnerProps, el, ChildProfileSelectPage()

### Community 33 - "Community 33"
Cohesion: 0.24
Nodes (4): SQLAlchemyRefreshTokenRepository, TokenResponse, login(), refresh_tokens()

### Community 34 - "Community 34"
Cohesion: 0.20
Nodes (4): LoginUseCase, BaseSettings, Config, Environment

### Community 35 - "Community 35"
Cohesion: 0.22
Nodes (5): create_app(), _seed_default_admin(), get_engine(), get_session(), _get_session_factory()

### Community 36 - "Community 36"
Cohesion: 0.24
Nodes (6): Recursively redact sensitive keys from a dict up to depth 5., Emit JSON log entries with all required fields., Configure the root logger with structured JSON output., _redact(), setup_logging(), StructuredFormatter

### Community 37 - "Community 37"
Cohesion: 0.38
Nodes (7): authPost(), login(), logout(), refreshToken(), register(), [url], [url, opts]

### Community 38 - "Community 38"
Cohesion: 0.20
Nodes (8): cardStyle, fieldStyle, inputStyle, labelStyle, LoginPage(), pageStyle, mockLogin, user

### Community 39 - "Community 39"
Cohesion: 0.24
Nodes (4): AuthProvider(), root, routeConfig, router

### Community 40 - "Community 40"
Cohesion: 0.31
Nodes (8): _compute(), generate_problem_set(), _is_duplicate(), _pick_operands(), _pick_operation(), _random_int(), create_rng(), Mulberry32 PRNG — Python port of the TypeScript implementation.      Applies a 3

### Community 41 - "Community 41"
Cohesion: 0.24
Nodes (8): AvatarCard(), AvatarCardProps, manageBtnStyle, menuItemStyle, menuStyle, starBtnStyle, useAvatarGallery(), AvatarGalleryPage()

### Community 42 - "Community 42"
Cohesion: 0.20
Nodes (3): KEYS, slider, toggle

### Community 43 - "Community 43"
Cohesion: 0.47
Nodes (8): get_config(), _check_database(), _check_redis(), _check_storage(), _get_db_engine(), _get_http_client(), _get_redis_client(), health()

### Community 44 - "Community 44"
Cohesion: 0.22
Nodes (7): b64url, HEADER, { mockSetAuthToken }, PAYLOAD, payloadObj, TestConsumer(), user

### Community 46 - "Community 46"
Cohesion: 0.29
Nodes (5): MusicTrack, inst, { result }, TRACK_FILES, useAudioManager()

### Community 50 - "Community 50"
Cohesion: 0.38
Nodes (5): _make_redis_client(), process_job(), Background worker — processes jobs from the Redis queue., Dispatch a job to the appropriate handler. Idempotent., run_worker()

### Community 51 - "Community 51"
Cohesion: 0.29
Nodes (3): AuthContext, AuthState, JwtPayload

### Community 52 - "Community 52"
Cohesion: 0.29
Nodes (6): clearIntervalSpy, pending, published, { result }, second, setIntervalSpy

### Community 53 - "Community 53"
Cohesion: 0.43
Nodes (6): AiObstacleResult, lerp(), sampleResponseTime(), simulateAiObstacle(), speedMultiplier(), AiPersonality

### Community 54 - "Community 54"
Cohesion: 0.33
Nodes (5): inst, paths, { result }, species, unique

### Community 55 - "Community 55"
Cohesion: 0.33
Nodes (4): BaseHTTPMiddleware, set_request_id(), CorrelationIdMiddleware, Generate a UUID correlation ID per request and inject it into the log context.

### Community 56 - "Community 56"
Cohesion: 0.40
Nodes (4): Card(), CardProps, onClick, user

### Community 57 - "Community 57"
Cohesion: 0.33
Nodes (4): LEGAL_TRANSITIONS, RaceStateError, transition(), RaceState

### Community 61 - "Community 61"
Cohesion: 0.67
Nodes (3): build_character_prompt(), Build a deterministic image generation prompt from avatar metadata.      attempt, VersionedPrompt

## Knowledge Gaps
- **281 isolated node(s):** `name`, `version`, `private`, `node`, `dev` (+276 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_run_pipeline()` connect `Community 28` to `Statistics Repository`, `Frontend Dependencies`, `Community 61`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `get_config()` connect `Community 43` to `Community 34`, `Community 35`, `Avatar Repository`, `Community 50`, `Community 28`, `Community 62`, `Community 63`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `PermissionError` connect `Avatar Domain Service` to `Community 33`, `Community 34`, `Achievement Evaluation`, `Statistics Repository`, `Child Profiles Backend`, `Community 48`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `Base` (e.g. with `PlayerStats` and `AvatarStats`) actually correct?**
  _`Base` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `StatisticsDomainService` (e.g. with `StatisticsRepository` and `RaceSession`) actually correct?**
  _`StatisticsDomainService` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `PermissionError` (e.g. with `_check_access()` and `delete_child_profile()`) actually correct?**
  _`PermissionError` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `version`, `private` to the rest of the system?**
  _304 weakly-connected nodes found - possible documentation gaps or missing edges._