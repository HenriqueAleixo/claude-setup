# CLAUDE SYSTEM RULES — Flutter Mobile (Professional Mode + TDD)

You are generating production-grade mobile applications with Flutter.

Platform:
- Flutter 3.x (stable channel)
- Dart SDK >=3.0.0 <4.0.0
- Target: Android + iOS (primary), Web/Desktop (secondary)
- State management: Bloc/Cubit
- DI: get_it + injectable
- Error handling: Either (dartz/fpdart)

---

# TDD WORKFLOW (MANDATORY — RED-GREEN-REFACTOR)

Every feature MUST follow TDD:

1. **RED**: Write a failing test FIRST
2. **GREEN**: Write the MINIMUM code to make it pass
3. **REFACTOR**: Clean up while keeping tests green

Rules:
- NEVER write implementation before the test exists
- Each test must fail for the RIGHT reason before implementing
- Show the test file BEFORE the implementation file
- One assertion per test (prefer)
- Tests must be deterministic and fast (< 1 second each)
- Test names in English, descriptive: `should return error when email is empty`

If asked to implement a feature without showing the test first, consider the solution invalid.

---

# ARCHITECTURE (MANDATORY — CLEAN ARCHITECTURE)

Three layers with strict dependency direction: Presentation → Domain → Data

```
lib/
├── core/
│   ├── error/
│   │   ├── failures.dart
│   │   └── exceptions.dart
│   ├── network/
│   │   └── network_info.dart
│   ├── usecases/
│   │   └── usecase.dart
│   ├── theme/
│   │   ├── app_theme.dart
│   │   ├── app_colors.dart
│   │   └── app_typography.dart
│   ├── routes/
│   │   └── app_router.dart
│   ├── utils/
│   │   ├── validators.dart
│   │   └── formatters.dart
│   └── constants/
│       └── app_constants.dart
├── features/
│   └── <feature_name>/
│       ├── data/
│       │   ├── datasources/
│       │   │   ├── <feature>_remote_datasource.dart
│       │   │   └── <feature>_local_datasource.dart
│       │   ├── models/
│       │   │   └── <feature>_model.dart
│       │   └── repositories/
│       │       └── <feature>_repository_impl.dart
│       ├── domain/
│       │   ├── entities/
│       │   │   └── <feature>.dart
│       │   ├── repositories/
│       │   │   └── <feature>_repository.dart
│       │   └── usecases/
│       │       └── get_<feature>.dart
│       └── presentation/
│           ├── bloc/
│           │   ├── <feature>_bloc.dart
│           │   ├── <feature>_event.dart
│           │   └── <feature>_state.dart
│           ├── pages/
│           │   └── <feature>_page.dart
│           └── widgets/
│               └── <feature>_card.dart
├── injection_container.dart
└── main.dart
```

Rules:
- Domain layer has ZERO dependencies on Flutter or external packages
- Domain entities are plain Dart classes (no annotations, no framework code)
- Data models extend/implement domain entities, handle serialization
- Repositories in domain are abstract; implementations live in data
- UseCases have a single `call()` method with Either return
- Presentation depends on domain only (never imports from data directly)
- Each feature is self-contained and independent

---

# ABSOLUTE PROHIBITIONS

NEVER:
- Use setState for anything beyond trivial local UI state (animations, toggle visibility)
- Create "god widgets" (build method > 80 lines)
- Put business logic in widgets or pages
- Use dynamic typing where static typing is possible
- Use print() for logging (use logger or dart:developer log())
- Hardcode strings, colors, dimensions, or durations (use constants/theme)
- Import data layer from presentation layer
- Import Flutter framework from domain layer
- Use late without guaranteed initialization
- Use ! (bang operator) without documented justification
- Catch generic Exception without specific handling
- Use FutureBuilder/StreamBuilder for complex state (use Bloc/Cubit)
- Store mutable state in global variables
- Skip null safety
- Use String concatenation for URLs (use Uri class)
- Nest widgets more than 4 levels deep in a single build method
- Create widgets without const constructor when possible
- Ignore BuildContext lifecycle (use context after async gap)
- Use global singletons without DI container

If any rule is broken, warn explicitly.

---

# SEPARATION OF CONCERNS (CRITICAL)

## Domain Layer (Pure Dart — ZERO framework imports)

Must:
- Be 100% framework-independent
- Contain only: entities, repository contracts (abstract), use cases, value objects
- Be fully testable with unit tests only
- Use Either<Failure, Success> for all use case returns
- Define Failure classes for each error category

Must NOT:
- Import package:flutter
- Import any external package except dartz/fpdart
- Contain serialization logic (fromJson/toJson)
- Know about Bloc, Provider, or any state management

## Data Layer

Must contain:
- Repository implementations (implements domain contracts)
- Data models (with fromJson/toJson, extends domain entity)
- Data sources: remote (API) and local (DB/cache)
- Network error → Exception → Failure mapping

## Presentation Layer

Must contain:
- Bloc/Cubit (state management, receives UseCases via constructor)
- Pages (full screens, compose widgets, provide Blocs)
- Widgets (reusable, single responsibility, < 80 lines build)
- No business logic — only dispatches events and reacts to states

---

# UI/UX QUALITY (MANDATORY)

Every screen must:
- Handle all states: Initial, Loading, Success, Empty, Error
- Show proper loading indicators (Shimmer preferred over CircularProgressIndicator)
- Display meaningful error messages with retry action
- Handle empty states with illustration + message + CTA
- Support pull-to-refresh where applicable
- Respect safe areas (SafeArea)
- Be responsive (LayoutBuilder / MediaQuery for breakpoints)

Visual quality:
- Use Material 3 (useMaterial3: true)
- Define complete ThemeData with ColorScheme, TextTheme, custom component themes
- Dark mode support from day one (ThemeMode.system)
- Consistent spacing via SizedBox or custom gap constants
- Animations: use AnimatedSwitcher, Hero, SlideTransition for polish
- Custom fonts defined in pubspec.yaml
- Adaptive design: platform-aware widgets when needed (Cupertino on iOS)

---

# STATE MANAGEMENT RULES (Bloc/Cubit)

Rules:
- One Bloc per feature/use-case (not per page)
- States must be immutable (use Equatable or freezed)
- Events must be immutable (use Equatable or freezed)
- Bloc must not depend on BuildContext
- Bloc must not import Flutter widgets
- Bloc receives UseCases via constructor injection
- Never emit state after Bloc is closed
- Use transformEvents/transformer for debounce on search/input

Cubit vs Bloc:
- Use Cubit for simple state (toggle, counter, form validation)
- Use Bloc for complex flows (authentication, multi-step, event-driven)

State pattern:
```dart
sealed class FeatureState extends Equatable {}
final class FeatureInitial extends FeatureState {}
final class FeatureLoading extends FeatureState {}
final class FeatureSuccess extends FeatureState { final Data data; }
final class FeatureFailure extends FeatureState { final String message; }
```

---

# DEPENDENCY INJECTION

- Use get_it as service locator
- Register all dependencies in injection_container.dart
- Lazy singleton for services, repositories, and data sources
- Factory for Blocs/Cubits (new instance per usage)
- Never access get_it directly from widgets (inject via BlocProvider)
- Initialize DI before runApp()

---

# NAVIGATION

- Use GoRouter (preferred) or auto_route
- Routes defined in core/routes/app_router.dart
- Use named routes with type-safe parameters
- Deep linking support required
- Never use Navigator.push with anonymous routes in production code
- Shell routes for bottom navigation / tabs

---

# PERSISTENCE RULES

- Local DB: sqflite or drift
- Key-value: shared_preferences (only for simple settings like theme, locale)
- Secure storage: flutter_secure_storage (tokens, credentials, API keys)
- Never store sensitive data in shared_preferences
- Never hardcode API URLs or keys (use --dart-define or .env)
- Cache strategy: local data source as offline fallback

---

# NETWORKING

- HTTP client: dio (preferred)
- Base client with interceptors: auth token, logging, retry, error mapping
- Timeout configuration mandatory (connect: 10s, receive: 15s)
- Retry logic for transient failures (503, timeout)
- Always consider offline fallback with local cache
- API responses mapped at data source level: JSON → Model → Entity
- Never expose raw Response objects beyond data source

---

# TESTING (MANDATORY — THREE LEVELS)

## Level 1: Unit Tests (domain + data)

- Test ALL UseCases (input → output via Either)
- Test ALL Repository implementations (remote/local delegation)
- Test ALL Models (fromJson, toJson, toEntity)
- Test ALL validators, formatters, pure logic
- Use mocktail for mocking
- Fixtures in test/fixtures/ as JSON files
- fixture_reader.dart helper for loading JSON

Pattern:
```dart
group('GetUser', () {
  test('should return User from repository', () async {
    // Arrange
    when(() => repository.getUser(any())).thenAnswer(
      (_) async => Right(tUser),
    );
    // Act
    final result = await usecase(Params(id: '1'));
    // Assert
    expect(result, Right(tUser));
    verify(() => repository.getUser('1')).called(1);
    verifyNoMoreInteractions(repository);
  });
});
```

## Level 2: Widget Tests (presentation)

- Test ALL Pages with different Bloc states
- Test ALL custom Widgets
- Test Bloc/Cubit with bloc_test package
- Use MockBloc/MockCubit from bloc_test
- Test: widget renders correct UI for each state
- Test: widget dispatches correct events on interaction
- Use pumpApp() helper for consistent MaterialApp wrapping

Pattern:
```dart
blocTest<FeatureBloc, FeatureState>(
  'emits [Loading, Success] when data is fetched',
  build: () {
    when(() => usecase(any())).thenAnswer(
      (_) async => Right(tData),
    );
    return FeatureBloc(usecase: usecase);
  },
  act: (bloc) => bloc.add(FetchFeature()),
  expect: () => [FeatureLoading(), FeatureSuccess(data: tData)],
);
```

## Level 3: Integration Tests

- Located in integration_test/
- Test complete user flows (login → home → detail → back)
- Use patrol or integration_test package
- Run with: `flutter test integration_test/`

## Mocking Rules

- Use mocktail (not mockito) — no codegen needed
- Create mock/fake classes in test/helpers/
- Every external dependency must be mockable (abstract class + DI)
- Never mock what you own when testing integration between your own layers

## Coverage Targets

- Domain layer: 100%
- Data layer: > 90%
- Presentation (Bloc): > 90%
- Presentation (Widgets): > 80%
- Run: `flutter test --coverage && genhtml coverage/lcov.info -o coverage/html`

---

# PACKAGES (RECOMMENDED STACK)

Core:
- flutter_bloc / bloc
- get_it
- dartz or fpdart
- equatable or freezed + freezed_annotation + build_runner
- go_router

Network:
- dio
- connectivity_plus

Persistence:
- sqflite or drift
- shared_preferences
- flutter_secure_storage

UI:
- shimmer
- cached_network_image
- flutter_svg
- google_fonts or custom fonts

Testing:
- mocktail
- bloc_test
- flutter_test (built-in)

Use these unless there is a documented reason to deviate.

---

# RELIABILITY

- Null safety is mandatory (no legacy opt-out)
- Error handling via Either pattern, not thrown exceptions across layers
- Loading/Error/Success/Empty states in every async operation
- All async operations must have timeout
- App must handle gracefully: no internet, slow connection, API errors, empty data
- Crashlytics or equivalent for production error tracking
- No overengineering
- No speculative abstraction
- No unnecessary wrapper layers

---

# RESPONSE FORMAT

When generating Flutter code:
1. Brief architecture explanation (max 10 lines)
2. Show IN THIS ORDER:
   a. Test file (RED phase — must fail)
   b. Implementation file (GREEN phase — make it pass)
   c. Refactoring notes if applicable
3. For each feature show layers inside-out: domain → data → presentation
4. No unused abstractions
5. No invented frameworks
6. Keep code deterministic and testable
7. Show dependency registration in injection_container.dart

---

# LANGUAGE

- Code: English
- Comments: Portuguese
- Communication: Brazilian Portuguese

If architecture violates these rules, consider the solution invalid.

---

# VALIDATION AFTER CODE CHANGES (MANDATORY)

After ANY code change, always:
1. Run `flutter analyze` to check for lint errors
2. Run `flutter test` to run all unit and widget tests
3. Run `flutter test --coverage` to verify coverage
4. Run on device/emulator with `flutter run` to confirm visually
5. Confirm the change worked correctly before considering the task done

Never leave a code change without running tests and analysis.
