import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { UserModule } from './user/user.module';
import { DataModule } from './data/data.module';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule } from '@nestjs/config';
import { DataRepository } from './data/data.repository';
import { DataSource } from 'typeorm';
import { DataService } from './data/data.service';
import { DataResolver } from './data/data.resolver';
import { Data } from './data/data.entity';

@Module({
	imports: [
		ConfigModule.forRoot({
			isGlobal: true,
		}),
		TypeOrmModule.forRoot({
			type: 'mysql',
			host: 'localhost',
			port: 3306,
			username: 'admin',
			password: 'Vanh@Mysql2006',
			database: 'typegraphql',
			synchronize: true,
			logging: true,
			connectorPackage: 'mysql2',
			autoLoadEntities: true,
			entities: [Data],
		}),
		TypeOrmModule.forFeature([DataRepository]),
		UserModule,
		DataModule,
		GraphQLModule.forRoot<ApolloDriverConfig>({
			autoSchemaFile: 'schema.gql',
			driver: ApolloDriver,
			installSubscriptionHandlers: true,
		}),
	],
	controllers: [AppController],
	providers: [AppService, DataResolver, DataService, DataRepository, DataSource],
})
export class AppModule {}
