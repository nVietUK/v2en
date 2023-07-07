import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { UserModule } from './user/user.module';
import { DataModule } from './data/data.module';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { TypeOrmModule, TypeOrmModuleOptions } from '@nestjs/typeorm';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { DataRepository } from './data/data.repository';
import { Data } from './data/data.entity';
import { IsDataExistedByHashValueConstraint } from './data/data.validator';

export const myConnectionOptions = async (
	configService: ConfigService,
): Promise<TypeOrmModuleOptions> => {
	return {
		type: 'mysql',
		host: configService.get('DB_HOST'),
		port: configService.get('DB_PORT'),
		username: configService.get('DB_USERNAME'),
		password: configService.get('DB_PASSWORD'),
		database: configService.get('DB_NAME'),
		synchronize: true,
		logging: true,
		autoLoadEntities: true,
		entities: [Data],
	};
};

@Module({
	imports: [
		ConfigModule.forRoot({
			isGlobal: true,
		}),
		TypeOrmModule.forRootAsync({
			imports: [ConfigModule],
			useFactory: myConnectionOptions,
			inject: [ConfigService],
		}),
		TypeOrmModule.forFeature([DataRepository, IsDataExistedByHashValueConstraint]),
		UserModule,
		DataModule,
		GraphQLModule.forRoot<ApolloDriverConfig>({
			autoSchemaFile: 'schema.gql',
			driver: ApolloDriver,
			installSubscriptionHandlers: true,
		}),
	],
	controllers: [AppController],
	providers: [AppService],
})
export class AppModule {}
