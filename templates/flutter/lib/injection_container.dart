import 'package:get_it/get_it.dart';

final sl = GetIt.instance;

Future<void> init() async {
  // TODO: registrar dependencies conforme features forem criadas
  //
  // Exemplo:
  // sl.registerFactory(() => FeatureBloc(usecase: sl()));
  // sl.registerLazySingleton(() => GetFeature(sl()));
  // sl.registerLazySingleton<FeatureRepository>(
  //   () => FeatureRepositoryImpl(remote: sl(), local: sl()),
  // );
}
