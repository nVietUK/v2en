import { Module } from '@nestjs/common';
import { DataController } from './data.controller';
import { DataService } from './data.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Data } from './data.entity';
import { DataRepository } from './data.repository';
import { DataResolver } from './data.resolver';

@Module({
	controllers: [DataController],
	providers: [DataService, DataRepository, DataResolver],
	imports: [TypeOrmModule.forFeature([Data])],
})
export class DataModule {}
