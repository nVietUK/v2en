import { Module } from '@nestjs/common';
import { DataResolver } from './data.resolver';
import { DataService } from './data.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Data } from './data.entity';
import { DataController } from './data.controller';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { DataRepository } from './data.repository';

@Module({
	providers: [DataResolver, DataService, DataRepository],
	imports: [TypeOrmModule.forFeature([Data])],
	controllers: [DataController],
})
export class DataModule {}
