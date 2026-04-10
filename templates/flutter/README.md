# {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}

## Setup

```bash
flutter pub get
flutter run
```

## Estrutura (Clean Architecture)

```
lib/
├── core/
│   ├── error/           # Failure, Exception
│   ├── network/         # NetworkInfo, dio client
│   ├── theme/           # ThemeData, cores, tipografia
│   ├── routes/          # GoRouter
│   └── constants/
├── features/
│   └── <feature>/
│       ├── data/        # datasources, models, repository_impl
│       ├── domain/      # entities, repository, usecases
│       └── presentation/# bloc, pages, widgets
└── main.dart
```

## Testes

```bash
flutter test                          # unit + widget
flutter test --coverage               # com cobertura
flutter test integration_test/        # e2e
```

## Metas de cobertura

- Domain: 100%
- Data: >90%
- Presentation (Bloc): >90%
- Presentation (Widgets): >80%
