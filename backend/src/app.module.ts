import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { UserModule } from './user/user.module';
import { DataModule } from './data/data.module';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { DirectiveLocation, GraphQLDirective } from 'graphql';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Data } from './data/data.entity';
import { ConfigModule, ConfigService } from '@nestjs/config';

@Module({
	imports: [
		ConfigModule.forRoot({
			isGlobal: true,
		}),
		TypeOrmModule.forRootAsync({
			imports: [ConfigModule],
			useFactory: async (configService: ConfigService) => ({
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
			}),
			inject: [ConfigService],
		}),
		TypeOrmModule.forFeature([Data]),
		UserModule,
		DataModule,
		GraphQLModule.forRoot<ApolloDriverConfig>({
			autoSchemaFile: 'schema.gql',
			driver: ApolloDriver,
			installSubscriptionHandlers: true,
			buildSchemaOptions: {
				directives: [
					new GraphQLDirective({
						name: 'upper',
						locations: [DirectiveLocation.FIELD_DEFINITION],
					}),
				],
			},
		}),
	],
	controllers: [AppController],
	providers: [AppService],
})
export class AppModule {}
